from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, ContactList, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.urls import reverse

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
        except:
            context['message'] = "An error occurred during login."

    return render(request, 'myapp/login.html', context)

def home2(request):
    return HttpResponse("<h1>Hello world 2<h1>")


# Show all contacts (admin/staff only)
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def showContact(request):
    allcontact = ContactList.objects.all().order_by('-id')
    context = {'contact': allcontact}
    return render(request, 'myapp/showcontact.html', context)


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
