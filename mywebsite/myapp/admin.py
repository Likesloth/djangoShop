from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *


# Customize the User admin so first/last name and email show on creation
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
        return user


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "first_name", "last_name", "email", "password1", "password2"),
        }),
    )


# Replace default User admin registration
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "instock")
    search_fields = ("title",)


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ("topic", "email", "complete")
    list_filter = ("complete",)
    search_fields = ("topic", "email")


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "complete", "created_at")
    list_filter = ("complete", "contact")
    search_fields = ("name", "detail", "contact__topic")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "usertype", "point")
    search_fields = ("user__username", "usertype")


# ==== Library registrations ====

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("full_name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn13", "publish_year", "language")
    search_fields = ("title", "isbn13")
    list_filter = ("language", "publish_year")


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ("book", "barcode", "status", "location")
    list_filter = ("status", "location")
    search_fields = ("barcode", "book__title", "book__isbn13")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("copy", "borrower", "checked_out_at", "due_at", "returned_at", "renew_count")
    list_filter = ("returned_at",)
    search_fields = ("copy__barcode", "borrower__username")
