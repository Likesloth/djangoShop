from django.urls import path
from .views import *

urlpatterns = [
    # Home now shows the shop landing page instead of the library grid
    path('', home, name="home-page"),
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
    # Auth and profile
    path('login/', userLogin, name="login"),
    path('logout/', userLogout, name="logout"),
    path('register/', userRegist, name="register"),
    path('profile/', userProfile, name="profile"),
    path('profile/edit/', editProfile, name="edit_profile"),
    path('settings/', settings_view, name="settings"),
    # Products
    path('addproduct/', addProduct, name="add-product"),
    # Catalog
    path('catalog/', catalog_list, name="catalog-list"),
    path('catalog/book/<int:book_id>/', book_detail, name="catalog-detail"),
    path('catalog/suggest-titles/', suggest_titles, name="suggest-titles"),
    # Cart + Requests
    path('cart/', cart_view, name='cart-view'),
    path('cart/add/<int:book_id>/', cart_add, name='cart-add'),
    path('cart/remove/<int:book_id>/', cart_remove, name='cart-remove'),
    path('cart/place-request/', cart_place_request, name='cart-place-request'),
    path('requests/mine/', my_requests, name='my-requests'),
    # Circulation
    path('circulation/loan/create/', loan_create, name="loan-create"),
    path('circulation/loan/<int:loan_id>/edit/', loan_update, name="loan-update"),
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
    # Staff: Requests workflow
    path('staff/requests/', requests_queue, name='staff-requests-queue'),
    path('staff/requests/<int:request_id>/', request_detail, name='staff-request-detail'),
    path('staff/requests/<int:request_id>/items/<int:item_id>/assign/', assign_item_copy, name='staff-request-assign-item'),
    path('staff/requests/<int:request_id>/items/<int:item_id>/unassign/', unassign_item_copy, name='staff-request-unassign-item'),
    path('staff/requests/<int:request_id>/ready/', mark_request_ready, name='staff-request-mark-ready'),
    path('staff/requests/<int:request_id>/pickup/', confirm_pickup, name='staff-request-confirm-pickup'),
    path('staff/requests/<int:request_id>/cancel/', cancel_request, name='staff-request-cancel'),
    # Staff: Loans by user
    path('staff/loans/', loans_by_user, name='staff-loans-by-user'),
]
