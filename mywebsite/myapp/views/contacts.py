from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from ..forms import ActionCreateForm, ActionUpdateForm, ActionQuickCreateForm
from ..models import Action, ContactList


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

