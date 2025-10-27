from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from myapp.models import Author, Book, BookCopy, Loan


class Command(BaseCommand):
    help = "Seed sample authors, books, copies, users, and an example loan. Safe to re-run."

    @transaction.atomic
    def handle(self, *args, **options):
        # Users
        librarian, created_lib = User.objects.get_or_create(
            username="librarian",
            defaults={"is_staff": True, "first_name": "Lib", "last_name": "Rarian"},
        )
        if created_lib:
            librarian.set_password("lib12345")
            librarian.save()

        student, created_student = User.objects.get_or_create(
            username="student",
            defaults={"first_name": "Stu", "last_name": "Dent"},
        )
        if created_student:
            student.set_password("student123")
            student.save()

        # Authors
        murakami, _ = Author.objects.get_or_create(full_name="Haruki Murakami")
        orwell, _ = Author.objects.get_or_create(full_name="George Orwell")
        austen, _ = Author.objects.get_or_create(full_name="Jane Austen")

        # Books
        b1, _ = Book.objects.get_or_create(
            isbn13="9780099448761",
            defaults={"title": "Norwegian Wood", "language": "EN", "publish_year": 1987},
        )
        b1.authors.add(murakami)

        b2, _ = Book.objects.get_or_create(
            isbn13="9780141036144",
            defaults={"title": "1984", "language": "EN", "publish_year": 1949},
        )
        b2.authors.add(orwell)

        b3, _ = Book.objects.get_or_create(
            isbn13="9781503290563",
            defaults={"title": "Pride and Prejudice", "language": "EN", "publish_year": 1813},
        )
        b3.authors.add(austen)

        # Copies (barcodes)
        copies_data = [
            (b1, ["BC-NW-001", "BC-NW-002"]),
            (b2, ["BC-1984-001", "BC-1984-002"]),
            (b3, ["BC-PAP-001"]),
        ]

        created_barcodes = []
        for book, barcodes in copies_data:
            for code in barcodes:
                copy, created = BookCopy.objects.get_or_create(
                    barcode=code,
                    defaults={"book": book, "location": "Main", "status": BookCopy.STATUS_AVAILABLE},
                )
                if created:
                    created_barcodes.append(code)

        # Example active loan: student borrows BC-1984-001
        try:
            copy_loan = BookCopy.objects.get(barcode="BC-1984-001")
            has_active = Loan.objects.filter(copy=copy_loan, returned_at__isnull=True).exists()
            if not has_active:
                loan = Loan.objects.create(
                    borrower=student,
                    copy=copy_loan,
                    due_at=timezone.now() + timedelta(days=14),
                    note="Seed loan",
                )
                copy_loan.status = BookCopy.STATUS_ON_LOAN
                copy_loan.save(update_fields=["status"])
                self.stdout.write(self.style.SUCCESS(f"Created loan: {loan}"))
        except BookCopy.DoesNotExist:
            pass

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write("Users:")
        self.stdout.write(" - librarian / lib12345 (staff)")
        self.stdout.write(" - student / student123")
        self.stdout.write("Barcodes:")
        self.stdout.write(" - BC-NW-001, BC-NW-002 (Norwegian Wood)")
        self.stdout.write(" - BC-1984-001, BC-1984-002 (1984)")
        self.stdout.write(" - BC-PAP-001 (Pride and Prejudice)")
        self.stdout.write("\nTry:")
        self.stdout.write(" - Open /catalog/ to see books and availability")
        self.stdout.write(" - Open /circulation/desk/?barcode=BC-1984-002 to quick checkout another copy")
