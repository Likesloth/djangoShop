from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from ..models import Profile


def userLogin(request):
    context = {}
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
            if not username:
                messages.error(request, 'Username is required.')
            elif username != request.user.username and User.objects.filter(username=username).exists():
                messages.error(request, 'This username is already taken.')
            else:
                user_to_update = request.user
                user_to_update.username = username
                user_to_update.first_name = first_name
                user_to_update.last_name = last_name
                user_to_update.email = email
                user_to_update.save()
                messages.success(request, 'Profile updated.')
        elif action == 'avatar':
            # File upload for avatar
            file = request.FILES.get('avatar')
            if not file:
                messages.error(request, 'Please choose an image to upload.')
            else:
                profile, _ = Profile.objects.get_or_create(user=request.user)
                # Optional: delete previous file to avoid orphaned media
                if getattr(profile, 'avatar', None) and profile.avatar:
                    try:
                        profile.avatar.delete(save=False)
                    except Exception:
                        pass
                profile.avatar = file
                profile.save()
                messages.success(request, 'Avatar updated.')
        elif action == 'avatar-remove':
            profile, _ = Profile.objects.get_or_create(user=request.user)
            if getattr(profile, 'avatar', None) and profile.avatar:
                try:
                    profile.avatar.delete(save=False)
                except Exception:
                    pass
                profile.avatar = None
                profile.save()
            messages.success(request, 'Avatar removed.')
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
