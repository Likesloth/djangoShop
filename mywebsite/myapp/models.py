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
    cover = models.ImageField(upload_to="images/", null=True, blank=True)
    authors = models.ManyToManyField(Author, related_name="books", blank=True)

    def __str__(self):
        return f"{self.title} ({self.isbn13})"


class BookCopy(models.Model):
    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_ON_LOAN = "ON_LOAN"
    STATUS_LOST = "LOST"
    STATUS_REPAIR = "REPAIR"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
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
