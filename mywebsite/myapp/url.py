from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name="home-page"),
    path('home2', home2, name="home2-page"),
    path('about/', aboutus, name="about-page"),
    path('contact/', contact, name="contact-page"),
    path('showcontacts/', showContact, name="showcontact-page"),
    # Use function-based login view and redirect by route name
    path('login/', userLogin, name="login"),
    path('logout/', userLogout, name="logout"),
    # Register and profile flows
    path('register/', userRegist, name="register"),
    path('profile/', userProfile, name="profile"),
    path('profile/edit/', editProfile, name="edit_profile"),
    # Redirect to home after logout for a smooth UX
    
]
