from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', library_home, name="home-page"),
    path('shop/', home, name="shop-home"),
    path('home2', home2, name="home2-page"),
    path('about/', aboutus, name="about-page"),
    path('contact/', contact, name="contact-page"),
    path('showcontacts/', showContact, name="showcontact-page"),
    path('contacts/<int:contact_id>/', contact_detail, name="contact-detail"),
    path('actions/create/', action_create, name="action-create"),
    path('contacts/<int:contact_id>/actions/new/', action_quick_create, name="action-quick-create"),
    path('actions/<int:action_id>/', actionPage, name="action-detail"),
    path('actions/<int:action_id>/edit/', action_update, name="action-update"),
    path('actions/<int:action_id>/delete/', action_delete, name="action-delete"),
    path('actions/<int:action_id>/toggle-complete/', action_toggle_complete, name="action-toggle-complete"),
    path('contacts/<int:contact_id>/toggle-complete/', contact_toggle_complete, name="contact-toggle-complete"),
    path('contacts/<int:contact_id>/delete/', delete_contact, name="contact-delete"),
    path('contacts/<int:contact_id>/actions-fragment/', contact_actions_fragment, name="contact-actions-fragment"),
    # Use function-based login view and redirect by route name
    path('login/', userLogin, name="login"),
    path('logout/', userLogout, name="logout"),
    path('addproduct/', addProduct, name="add-product"),
    # Register and profile flows
    path('register/', userRegist, name="register"),
    path('profile/', userProfile, name="profile"),
    path('profile/edit/', editProfile, name="edit_profile"),
    path('settings/', settings_view, name="settings"),
    # Redirect to home after logout for a smooth UX
    # Catalog (Library)
    path('catalog/', catalog_list, name="catalog-list"),
    path('catalog/book/<int:book_id>/', book_detail, name="catalog-detail"),
    # Circulation (Library)
    path('circulation/loan/create/', loan_create, name="loan-create"),
    path('circulation/loan/<int:loan_id>/edit/', loan_update, name="loan-update"),
    path('circulation/desk/', quick_checkout, name="circulation-desk"),
    path('loans/mine/', my_loans, name="my-loans"),
    path('fines/mine/', my_fines, name="my-fines"),
    # Staff tools
    path('staff/overdues/', overdues_list, name='staff-overdues'),
    path('staff/fines/', fines_ledger, name='staff-fines'),
    path('staff/fines/<int:fine_id>/paid/', fine_mark_paid, name='staff-fine-paid'),
    path('staff/books/new/', book_create_manual, name='staff-book-create'),
    path('staff/reports/', reports_dashboard, name='staff-reports'),
    path('staff/reports/overdues.csv', report_overdues_csv, name='report-overdues-csv'),
    path('staff/reports/top-borrowed.csv', report_top_borrowed_csv, name='report-top-borrowed-csv'),
    path('staff/reports/fines-summary.csv', report_fines_summary_csv, name='report-fines-summary-csv'),
    path('staff/copy/<int:copy_id>/status/<str:status>/', copy_status_update, name='staff-copy-status'),
]
