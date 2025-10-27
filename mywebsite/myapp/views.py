from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ActionCreateForm, ActionUpdateForm, ActionQuickCreateForm
from .models import Action, ContactList, Product, Profile


# Create your views here.

def home(request):
    all_products = Product.objects.all().order_by('-id')
    paginator = Paginator(all_products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "myapp/pages/home.html", {"allproduct": page_obj})


def aboutus(request):
    return render(request, "myapp/pages/aboutus.html")


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

    return render(request, 'myapp/pages/contact.html', context)


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

    return render(request, 'myapp/auth/login.html', context)


def home2(request):
    return HttpResponse("<h1>Hello world 2<h1>")


# Show all contacts (admin/staff only)
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def showContact(request):
    contacts_qs = ContactList.objects.all().order_by('-id').prefetch_related('actions')

    paginator = Paginator(contacts_qs, 10)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)

    selected_contact = None
    contact_id = request.GET.get('contact')
    if contact_id:
        selected_contact = get_object_or_404(ContactList, id=contact_id)
    else:
        # Default to the first contact on the current page (if any)
        try:
            selected_contact = contacts[0]
        except IndexError:
            selected_contact = None

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
    return render(request, 'myapp/contacts/showcontact.html', context)


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

    return render(request, 'myapp/actions/action_form.html', {'form': form, 'title': 'Create Action'})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def actionPage(request, action_id):
    action = get_object_or_404(Action.objects.select_related('contact'), id=action_id)
    return render(request, 'myapp/actions/action.html', {'action': action})


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

    return render(request, 'myapp/actions/action_form.html', {'form': form, 'title': 'Update Action', 'action': action})


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

    return render(request, 'myapp/actions/action_confirm_delete.html', {'action': action})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def action_toggle_complete(request, action_id):
    action = get_object_or_404(Action, id=action_id)
    if request.method == 'POST':
        complete_value = (request.POST.get('complete') or '').strip().lower()
        action.complete = complete_value in ('1', 'true', 'yes', 'on')
        action.save(update_fields=['complete'])
        status_label = 'marked complete' if action.complete else 'marked pending'
        messages.success(request, f'Action {status_label}.')
    return redirect('action-detail', action_id=action.id)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def action_quick_create(request, contact_id):
    contact = get_object_or_404(ContactList, id=contact_id)
    if request.method == 'POST':
        form = ActionQuickCreateForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.contact = contact
            action.save()
            messages.success(request, 'Action created successfully.')
            return redirect(f"{reverse('showcontact-page')}?contact={contact.id}")
    else:
        form = ActionQuickCreateForm()
    return render(request, 'myapp/actions/action_quick_create.html', {'form': form, 'contact': contact})


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

    return render(request, 'myapp/contacts/contact_confirm_delete.html', {'contact': contact})


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

    return render(request, 'myapp/auth/register.html', context)


@login_required(login_url='login')
def userProfile(request):
    # Redirect legacy profile page to consolidated settings
    return redirect('settings')


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

    return render(request, 'myapp/profile/editprofile.html')


@login_required(login_url='login')
def settings_view(request):
    context = {}
    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()
        if action == 'profile':
            data = request.POST
            username = (data.get('username') or '').strip()
            first_name = (data.get('first_name') or '').strip()
            last_name = (data.get('last_name') or '').strip()
            email = (data.get('email') or '').strip()

            # Basic validation
            if not username:
                messages.error(request, 'Username is required.')
            elif username != request.user.username and User.objects.filter(username=username).exists():
                messages.error(request, 'This username is already taken.')
            else:
                u = request.user
                u.username = username
                u.first_name = first_name
                u.last_name = last_name
                u.email = email
                u.save()
                messages.success(request, 'Profile updated.')

        elif action == 'password':
            current_password = (request.POST.get('current_password') or '').strip()
            new_password = (request.POST.get('new_password') or '').strip()
            confirm_password = (request.POST.get('confirm_password') or '').strip()

            user = authenticate(username=request.user.username, password=current_password)
            if user is None:
                messages.error(request, 'Current password is incorrect.')
            elif not new_password:
                messages.error(request, 'New password is required.')
            elif new_password != confirm_password:
                messages.error(request, 'New password and confirm password do not match.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password updated.')

    return render(request, 'myapp/profile/settings.html', context)


def userLogout(request):
    logout(request)
    return redirect('login')
def addProduct(request):
    if request.method == "POST":
        product = Product(
            title=request.POST.get('title', '').strip(),
            description=request.POST.get('description', ''),
            price=request.POST.get('price') or None,
            quantity=request.POST.get('quantity') or None,
            picture=request.FILES.get('picture'),
            specfile=request.FILES.get('specfile')
        )
        product.save()
        return redirect('home-page')
    return render(request, "myapp/products/addProduct.html")


def handler404(request, exception):
    return render(request, "myapp/pages/404errorPage.html", status=404)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def contact_detail(request, contact_id):
    contact = get_object_or_404(ContactList, id=contact_id)
    actions = contact.actions.all().order_by('-updated_at')

    if request.method == 'POST':
        form = ActionQuickCreateForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.contact = contact
            action.save()
            messages.success(request, 'Action created successfully.')
            return redirect('contact-detail', contact_id=contact.id)
    else:
        form = ActionQuickCreateForm()

    return render(request, 'myapp/contacts/contact_detail.html', {
        'contact': contact,
        'actions': actions,
        'form': form,
    })


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def contact_actions_fragment(request, contact_id):
    contact = get_object_or_404(ContactList, id=contact_id)
    actions = contact.actions.all().order_by('-updated_at')
    html = render_to_string('myapp/actions/_actions_list.html', {'actions': actions}, request=request)
    return JsonResponse({
        'ok': True,
        'topic': contact.topic,
        'html': html,
        'new_url': reverse('action-quick-create', args=[contact.id]),
    })
