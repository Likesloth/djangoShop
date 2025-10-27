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
from .circulation import loan_create, loan_update, quick_checkout
from .account import my_loans, my_fines

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
    "loan_create", "loan_update", "quick_checkout",
    # account
    "my_loans", "my_fines",
]
