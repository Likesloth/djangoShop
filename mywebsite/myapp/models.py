from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(default=0, null=True, blank=True)
    instock = models.BooleanField(default=True)
    picture = models.ImageField(upload_to="images/", null=True, blank=True)
    specfile = models.FileField(upload_to="specs/", null=True, blank=True)

    def __str__(self):
        return self.title


class ContactList(models.Model):
    topic = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    detail = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return self.topic


class Action(models.Model):
    contact = models.ForeignKey(ContactList, on_delete=models.CASCADE, related_name='actions')
    name = models.CharField(max_length=200)
    detail = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at', '-created_at']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usertype = models.CharField(max_length=100, default='member')
    point = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


# ==== Library System (MVP) ====

class Author(models.Model):
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name


class Book(models.Model):
    isbn13 = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50, blank=True)
    publish_year = models.PositiveIntegerField(null=True, blank=True)
    cover = models.ImageField(upload_to="images/books/", null=True, blank=True)
    authors = models.ManyToManyField(Author, related_name="books", blank=True)
    # Classification
    # Category: hierarchical navigation
    # Tag: flexible many-to-many labels for filtering
    # Added for catalog navigation and filters
    
    # Declared below but referenced here via strings to avoid ordering issues
    category = models.ForeignKey("Category", null=True, blank=True, on_delete=models.SET_NULL, related_name="books")
    tags = models.ManyToManyField("Tag", blank=True, related_name="books")

    def __str__(self):
        return f"{self.title} ({self.isbn13})"


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BookCopy(models.Model):
    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_RESERVED = "RESERVED"  # reserved for pickup
    STATUS_ON_LOAN = "ON_LOAN"
    STATUS_LOST = "LOST"
    STATUS_REPAIR = "REPAIR"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_ON_LOAN, "On loan"),
        (STATUS_LOST, "Lost"),
        (STATUS_REPAIR, "Repair"),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    barcode = models.CharField(max_length=64, unique=True)
    location = models.CharField(max_length=120, blank=True)
    condition_note = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    def __str__(self):
        return f"{self.book.title} [{self.barcode}]"


class Loan(models.Model):
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="loans")
    copy = models.ForeignKey(BookCopy, on_delete=models.PROTECT, related_name="loans")
    checked_out_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    renew_count = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-checked_out_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["copy", "returned_at"],
                name="unique_active_loan_per_copy",
                condition=models.Q(returned_at=None),
            )
        ]

    def __str__(self):
        return f"{self.copy.barcode} → {self.borrower} (due {self.due_at:%Y-%m-%d})"




from decimal import Decimal


class Fine(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="fines")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "paid" if self.paid_at else "unpaid"
        return f"Fine {self.amount} ({status}) for loan {self.loan_id}"


class Policy(models.Model):
    # Single-row table to allow admin to tweak policies without code changes
    student_loan_limit = models.PositiveIntegerField(default=5)
    lecturer_loan_limit = models.PositiveIntegerField(default=10)
    student_loan_days = models.PositiveIntegerField(default=14)
    lecturer_loan_days = models.PositiveIntegerField(default=28)
    fine_rate_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("5.00"))

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Library Policy"

    @classmethod
    def current(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj


# ==== Cart and Pickup Request (MVP) ====


class Cart(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} by {self.owner}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "book")

    def __str__(self):
        return f"{self.book.title} in cart {self.cart_id}"


class PickupRequest(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_PREPARING = "PREPARING"
    STATUS_READY = "READY"
    STATUS_PICKED_UP = "PICKED_UP"
    STATUS_CANCELED = "CANCELED"
    STATUS_EXPIRED = "EXPIRED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PREPARING, "Preparing"),
        (STATUS_READY, "Ready for pickup"),
        (STATUS_PICKED_UP, "Picked up"),
        (STATUS_CANCELED, "Canceled"),
        (STATUS_EXPIRED, "Expired"),
    ]

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pickup_requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    pickup_location = models.CharField(max_length=120, blank=True)
    pickup_by = models.DateField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Request #{self.id} by {self.requester} ({self.status})"


class PickupRequestItem(models.Model):
    request = models.ForeignKey(PickupRequest, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    # Staff may assign a specific copy during preparation
    assigned_copy = models.ForeignKey(BookCopy, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_in_requests")
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("request", "book")

    def __str__(self):
        base = f"{self.book.title} in request {self.request_id}"
        if self.assigned_copy_id:
            return f"{base} -> {self.assigned_copy.barcode}"
        return base
