from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name="home-page"),
    path('home2', home2, name="home2-page"),
    path('about/', aboutus, name="about-page"),
    path('contact/', contact, name="contact-page"),
    path('showcontacts/', showContact, name="showcontact-page"),
    path('actions/create/', action_create, name="action-create"),
    path('actions/<int:action_id>/', actionPage, name="action-detail"),
    path('actions/<int:action_id>/edit/', action_update, name="action-update"),
    path('actions/<int:action_id>/delete/', action_delete, name="action-delete"),
    path('contacts/<int:contact_id>/toggle-complete/', contact_toggle_complete, name="contact-toggle-complete"),
    path('contacts/<int:contact_id>/delete/', delete_contact, name="contact-delete"),
    # Use function-based login view and redirect by route name
    path('login/', userLogin, name="login"),
    path('logout/', userLogout, name="logout"),
    path('addproduct/', addProduct, name="add-product"),
    # Register and profile flows
    path('register/', userRegist, name="register"),
    path('profile/', userProfile, name="profile"),
    path('profile/edit/', editProfile, name="edit_profile"),
    # Redirect to home after logout for a smooth UX
    
]
