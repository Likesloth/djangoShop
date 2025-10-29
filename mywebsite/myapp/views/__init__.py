from .home import home, library_home, aboutus, contact, home2, handler404, addProduct
from .auth import userLogin, userLogout, userRegist, userProfile, editProfile, settings_view
from .contacts import (
    showContact,
    action_create,
    action_quick_create,
    actionPage,
    action_update,
    action_delete,
    action_toggle_complete,
    contact_toggle_complete,
    delete_contact,
    contact_detail,
    contact_actions_fragment,
)
from .catalog import catalog_list, book_detail
from .circulation import loan_create, loan_update
from .account import my_loans, my_fines
from .cart import cart_view, cart_add, cart_remove, cart_place_request
from .requests import (
    my_requests,
    requests_queue,
    request_detail,
    assign_item_copy,
    unassign_item_copy,
    mark_request_ready,
    confirm_pickup,
    cancel_request,
)
from .staff import (
    copy_status_update,
    overdues_list,
    fines_ledger,
    fine_mark_paid,
    book_create_manual,
    reports_dashboard,
    report_overdues_csv,
    report_top_borrowed_csv,
    report_fines_summary_csv,
    loans_by_user,
)

__all__ = [
    # home
    "home", "library_home", "aboutus", "contact", "home2", "handler404", "addProduct",
    # auth
    "userLogin", "userLogout", "userRegist", "userProfile", "editProfile", "settings_view",
    # contacts/actions
    "showContact", "action_create", "actionPage", "action_update", "action_delete",
    "action_quick_create", "action_toggle_complete", "contact_toggle_complete", "delete_contact", "contact_detail",
    "contact_actions_fragment",
    # catalog
    "catalog_list", "book_detail",
    # circulation
    "loan_create", "loan_update",
    # account
    "my_loans", "my_fines",
    # cart + requests
    "cart_view", "cart_add", "cart_remove", "cart_place_request",
    "my_requests", "requests_queue", "request_detail", "assign_item_copy", "unassign_item_copy", "mark_request_ready", "confirm_pickup", "cancel_request",
    # staff
    "copy_status_update", "overdues_list", "fines_ledger", "fine_mark_paid", "book_create_manual", "reports_dashboard",
    "report_overdues_csv", "report_top_borrowed_csv", "report_fines_summary_csv", "loans_by_user",
]

