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
    list_display = ("title", "isbn13", "publish_year", "language", "category")
    search_fields = ("title", "isbn13", "authors__full_name")
    list_filter = ("language", "publish_year", "category")


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


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("loan", "amount", "created_at", "paid_at")
    list_filter = ("paid_at",)
    search_fields = ("loan__copy__barcode", "loan__borrower__username")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "slug")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")




@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ("student_loan_limit", "lecturer_loan_limit", "student_loan_days", "lecturer_loan_days", "fine_rate_per_day", "updated_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "created_at", "updated_at")
    search_fields = ("owner__username",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "book", "added_at")
    search_fields = ("cart__owner__username", "book__title")


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "requester", "status", "pickup_location", "pickup_by", "requested_at", "ready_at", "picked_up_at")
    list_filter = ("status", "pickup_location")
    search_fields = ("requester__username",)


@admin.register(PickupRequestItem)
class PickupRequestItemAdmin(admin.ModelAdmin):
    list_display = ("request", "book", "assigned_copy")
    search_fields = ("request__requester__username", "book__title", "assigned_copy__barcode")
