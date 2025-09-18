from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ActionCreateForm, ActionUpdateForm
from .models import Action, ContactList, Product, Profile


# Create your views here.

def home(request):
    allproduct = Product.objects.all()
    context = {"pd": allproduct}
    return render(request, "myapp/home.html", context)


def aboutus(request):
    return render(request, "myapp/aboutus.html")


def contact(request):
    context = {}  # message to notify

    if request.method == 'POST':
        data = request.POST
        topic = (data.get('topic') or '').strip()
        email = (data.get('email') or '').strip()
        detail = (data.get('detail') or '').strip()

        # Preserve submitted values (if template uses them later)
        context.update({'topic': topic, 'email': email, 'detail': detail})

        # Validate required fields
        if topic and email and detail:
            ContactList.objects.create(topic=topic, email=email, detail=detail)
            context['message'] = 'The message has been received'
        else:
            context['message'] = 'Please fill in all fields: topic, email, and detail.'

    return render(request, 'myapp/contact.html', context)


def userLogin(request):
    context = {}

    # Show success notice after registration
    if request.method == 'GET' and request.GET.get('registered') == '1':
        context['message'] = 'Account created. You can now log in.'
        context['registered'] = True

    if request.method == 'POST':
        data = request.POST.copy()
        username = data.get('username')
        password = data.get('password')

        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home-page')
            else:
                context['message'] = "Username or password is incorrect."
        except Exception:
            context['message'] = "An error occurred during login."

    return render(request, 'myapp/login.html', context)


def home2(request):
    return HttpResponse("<h1>Hello world 2<h1>")


# Show all contacts (admin/staff only)
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def showContact(request):
    contacts = ContactList.objects.all().order_by('-id').prefetch_related('actions')
    selected_contact = None

    contact_id = request.GET.get('contact')
    if contact_id:
        selected_contact = get_object_or_404(ContactList, id=contact_id)
    else:
        selected_contact = contacts.first()

    if selected_contact:
        actions = selected_contact.actions.all().order_by('-created_at')
        create_form_initial = {'contact': selected_contact.id}
    else:
        actions = Action.objects.none()
        create_form_initial = None

    create_form = ActionCreateForm(initial=create_form_initial)

    context = {
        'contacts': contacts,
        'selected_contact': selected_contact,
        'actions': actions,
        'create_form': create_form,
    }
    return render(request, 'myapp/showcontact.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def action_create(request):
    if request.method == 'POST':
        form = ActionCreateForm(request.POST)
        if form.is_valid():
            action = form.save()
            messages.success(request, 'Action created successfully.')
            return redirect('action-detail', action_id=action.id)
    else:
        initial = {}
        contact_id = request.GET.get('contact')
        if contact_id:
            contact = ContactList.objects.filter(id=contact_id).first()
            if contact:
                initial['contact'] = contact
        form = ActionCreateForm(initial=initial)

    return render(request, 'myapp/action_form.html', {'form': form, 'title': 'Create Action'})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def actionPage(request, action_id):
    action = get_object_or_404(Action.objects.select_related('contact'), id=action_id)
    return render(request, 'myapp/action.html', {'action': action})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def action_update(request, action_id):
    action = get_object_or_404(Action, id=action_id)

    if request.method == 'POST':
        form = ActionUpdateForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            messages.success(request, 'Action updated successfully.')
            return redirect('action-detail', action_id=action.id)
    else:
        form = ActionUpdateForm(instance=action)

    return render(request, 'myapp/action_form.html', {'form': form, 'title': 'Update Action', 'action': action})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def action_delete(request, action_id):
    action = get_object_or_404(Action, id=action_id)
    redirect_contact = action.contact_id

    if request.method == 'POST':
        action.delete()
        messages.success(request, 'Action deleted successfully.')
        if redirect_contact:
            target = f"{reverse('showcontact-page')}?contact={redirect_contact}"
            return redirect(target)
        return redirect('showcontact-page')

    return render(request, 'myapp/action_confirm_delete.html', {'action': action})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def contact_toggle_complete(request, contact_id):
    contact = get_object_or_404(ContactList, id=contact_id)

    if request.method == "POST":
        complete_value = (request.POST.get('complete') or '').strip().lower()
        contact.complete = complete_value in ('1', 'true', 'yes', 'on')
        contact.save(update_fields=['complete'])
        status_label = 'marked complete' if contact.complete else 'marked pending'
        messages.success(request, f'Contact {status_label}.')
    return redirect(f"{reverse('showcontact-page')}?contact={contact.id}")



@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def delete_contact(request, contact_id):
    contact = get_object_or_404(ContactList, id=contact_id)

    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact deleted successfully.')
        return redirect('showcontact-page')

    return render(request, 'myapp/contact_confirm_delete.html', {'contact': contact})


def userRegist(request):
    context = {}
    if request.method == 'POST':
        data = request.POST.copy()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        first_name = (data.get('first_name') or '').strip()
        last_name = (data.get('last_name') or '').strip()
        email = (data.get('email') or '').strip()

        if not username or not password:
            context['message'] = 'Username and password are required.'
        elif User.objects.filter(username=username).exists():
            context['message'] = 'Username already exists.'
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                )
                Profile.objects.create(user=user)
                context['message'] = 'Account created. You can now log in.'
                context['success'] = True
            except Exception:
                context['message'] = 'Failed to create account.'

    return render(request, 'myapp/register.html', context)


@login_required(login_url='login')
def userProfile(request):
    return render(request, 'myapp/profile.html')


@login_required(login_url='login')
def editProfile(request):
    if request.method == 'POST':
        data = request.POST.copy()
        user = request.user
        user.first_name = (data.get('first_name') or '').strip()
        user.last_name = (data.get('last_name') or '').strip()
        user.email = (data.get('email') or '').strip()
        user.save()
        return redirect('profile')

    return render(request, 'myapp/editprofile.html')


def userLogout(request):
    logout(request)
    return redirect('login')
