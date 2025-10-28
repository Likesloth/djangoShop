from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.conf import settings
from pathlib import Path
from django.utils import timezone
from django.utils.text import slugify

from ...models import (
    Author,
    Book,
    BookCopy,
    Category,
    Tag,
    Loan,
    Fine,
    Cart,
    CartItem,
    PickupRequest,
    PickupRequestItem,
)


DATASET = [
    # Use this shape everywhere:
    # (isbn13, title, authors, category_path, tags, language, year, copies)
    ("9780135957059", "The Pragmatic Programmer", ["Andrew Hunt", "David Thomas"], "Technology > Software", ["Programming", "Best Practices"], "EN", 1999, 4),
    ("9780132350884", "Clean Code", ["Robert C. Martin"], "Technology > Software", ["Programming", "Code Quality"], "EN", 2008, 5),
    ("9780262033848", "Introduction to Algorithms", ["Thomas H. Cormen", "Charles E. Leiserson", "Ronald L. Rivest", "Clifford Stein"], "Technology > Computer Science", ["Algorithms", "Textbook"], "EN", 2009, 3),
    ("9780201633610", "Design Patterns", ["Erich Gamma", "Richard Helm", "Ralph Johnson", "John Vlissides"], "Technology > Software", ["Patterns", "Architecture"], "EN", 1994, 3),
    ("9780262035613", "Deep Learning", ["Ian Goodfellow", "Yoshua Bengio", "Aaron Courville"], "Technology > AI/ML", ["AI", "Neural Networks"], "EN", 2016, 2),
    ("9781593276034", "Python Crash Course", ["Eric Matthes"], "Technology > Software", ["Python", "Beginner"], "EN", 2015, 5),
    ("9781491946008", "Fluent Python", ["Luciano Ramalho"], "Technology > Software", ["Python", "Advanced"], "EN", 2015, 3),
    ("9780134685991", "Effective Java", ["Joshua Bloch"], "Technology > Software", ["Java", "Best Practices"], "EN", 2017, 3),
    ("9781617292231", "Grokking Algorithms", ["Aditya Bhargava"], "Technology > Computer Science", ["Algorithms", "Illustrated"], "EN", 2016, 4),
    ("9798602477429", "You Don't Know JS Yet", ["Kyle Simpson"], "Technology > Software", ["JavaScript"], "EN", 2020, 3),
    ("9780201835953", "The Mythical Man-Month", ["Frederick P. Brooks Jr."], "Technology > Software", ["Management"], "EN", 1975, 2),
    ("9780134757599", "Refactoring", ["Martin Fowler"], "Technology > Software", ["Refactoring", "Code Quality"], "EN", 2018, 4),
    ("9780136042594", "Artificial Intelligence: A Modern Approach", ["Stuart Russell", "Peter Norvig"], "Technology > AI/ML", ["AI", "Textbook"], "EN", 2010, 2),
    ("9780262510875", "Structure and Interpretation of Computer Programs", ["Harold Abelson", "Gerald Jay Sussman", "Julie Sussman"], "Technology > Computer Science", ["CS", "Lisp"], "EN", 1996, 2),
    ("9780137081073", "The Clean Coder", ["Robert C. Martin"], "Technology > Software", ["Professionalism"], "EN", 2011, 3),
    ("9780988262591", "The Phoenix Project", ["Gene Kim", "Kevin Behr", "George Spafford"], "Business > IT", ["DevOps", "Novel"], "EN", 2013, 3),
    ("9780321601919", "Continuous Delivery", ["Jez Humble", "David Farley"], "Technology > Software", ["DevOps", "CI/CD"], "EN", 2010, 2),
    ("9780321125217", "Domain-Driven Design", ["Eric Evans"], "Technology > Software", ["DDD", "Architecture"], "EN", 2003, 3),
    ("9780131177055", "Working Effectively with Legacy Code", ["Michael Feathers"], "Technology > Software", ["Legacy", "Refactoring"], "EN", 2004, 2),
    ("9780984782857", "Cracking the Coding Interview", ["Gayle Laakmann McDowell"], "Technology > Careers", ["Interview", "Practice"], "EN", 2015, 4),
    ("9780465050659", "The Design of Everyday Things", ["Don Norman"], "Design > UX", ["Design", "Usability"], "EN", 2013, 3),
    ("9780321965516", "Don't Make Me Think", ["Steve Krug"], "Design > UX", ["Usability", "Web"], "EN", 2014, 2),
    ("9780201896831", "The Art of Computer Programming Vol. 1", ["Donald E. Knuth"], "Technology > Computer Science", ["Algorithms", "Theory"], "EN", 2011, 2),
    ("9780201896848", "The Art of Computer Programming Vol. 2", ["Donald E. Knuth"], "Technology > Computer Science", ["Algorithms", "Theory"], "EN", 2011, 2),
    ("9780201896855", "The Art of Computer Programming Vol. 3", ["Donald E. Knuth"], "Technology > Computer Science", ["Algorithms", "Theory"], "EN", 2011, 2),
    ("9780553103748", "A Brief History of Time", ["Stephen Hawking"], "Science > Physics", ["Cosmology"], "EN", 1998, 3),
    ("9780062316097", "Sapiens: A Brief History of Humankind", ["Yuval Noah Harari"], "History", ["Anthropology", "Civilization"], "EN", 2015, 3),
    ("9780374533557", "Thinking, Fast and Slow", ["Daniel Kahneman"], "Psychology", ["Behavioral", "Decision Making"], "EN", 2011, 3),
    ("9780735211292", "Atomic Habits", ["James Clear"], "Self-Help", ["Habits", "Productivity"], "EN", 2018, 4),
    ("9780547928227", "The Hobbit", ["J.R.R. Tolkien"], "Fiction > Fantasy", ["Fantasy", "Classic"], "EN", 1937, 5),
]


def _ensure_category(path_str):
    if not path_str:
        return None
    names = [p.strip() for p in path_str.split('>') if p.strip()]
    parent = None
    for name in names:
        obj, _ = Category.objects.get_or_create(slug=slugify(name), defaults={"name": name, "parent": parent})
        if obj.parent_id != (parent.id if parent else None):
            obj.parent = parent
            obj.save(update_fields=["parent"])
        parent = obj
    return parent


def wipe_domain():
    """Delete domain objects in FK-safe order. Temporarily disable constraint
    checking at the DB level to accommodate SQLite behavior.
    """
    checks_disabled = connection.disable_constraint_checking()
    try:
        # Requests and carts first (depend on books/copies)
        PickupRequestItem.objects.update(assigned_copy=None)
        PickupRequestItem.objects.all().delete()
        PickupRequest.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()

        # Fines and loans (depend on copies)
        Fine.objects.all().delete()
        Loan.objects.all().delete()

        # Clear M2M through tables explicitly before deleting main tables
        Book.authors.through.objects.all().delete()
        Book.tags.through.objects.all().delete()

        # Copies then books
        BookCopy.objects.all().delete()
        Book.objects.all().delete()

        # Taxonomy
        Tag.objects.all().delete()
        Category.objects.all().delete()
        Author.objects.all().delete()
    finally:
        if checks_disabled:
            connection.enable_constraint_checking()


class Command(BaseCommand):
    help = "Reset library catalog with 30 curated books, multiple copies, categories, and tags."

    def add_arguments(self, parser):
        parser.add_argument(
            "--drop-existing",
            action="store_true",
            help="Delete existing catalog (loans, copies, books, categories, tags, carts, requests).",
        )

    def handle(self, *args, **options):
        drop = options.get("drop_existing")
        if drop:
            self.stdout.write(self.style.WARNING("Dropping existing library domain objects..."))
            wipe_domain()
        else:
            # Even without drop, avoid duplicates by de-duplicating on isbn13
            pass

        # Seed dataset
        created_books = 0
        for (isbn13, title, authors, cat_path, tags, lang, year, copies) in DATASET:
            cat = _ensure_category(cat_path)
            book, created = Book.objects.get_or_create(
                isbn13=isbn13,
                defaults={
                    "title": title,
                    "language": lang,
                    "publish_year": year,
                    "category": cat,
                },
            )
            if not created:
                # Update basic fields if book exists
                book.title = title
                book.language = lang
                book.publish_year = year
                book.category = cat
                book.save()

            # Authors
            for full_name in authors:
                a, _ = Author.objects.get_or_create(full_name=full_name)
                book.authors.add(a)

            # Tags
            for name in tags:
                tag, _ = Tag.objects.get_or_create(slug=slugify(name), defaults={"name": name})
                book.tags.add(tag)

            # Copies (ensure 2-5 copies as requested in dataset)
            for c in range(1, int(copies) + 1):
                barcode = f"BC{isbn13}-{c:02d}"
                BookCopy.objects.get_or_create(
                    barcode=barcode,
                    defaults={
                        "book": book,
                        "location": "Main",
                        "status": BookCopy.STATUS_AVAILABLE,
                    },
                )
            created_books += 1 if created else 0

            # Attach cover image if available at media/images/books/<isbn13>.(jpg|jpeg|png|webp)
            try:
                covers_dir = Path(settings.MEDIA_ROOT) / 'images' / 'books'
                for ext in ('.jpg', '.jpeg', '.png', '.webp'):
                    fp = covers_dir / f"{isbn13}{ext}"
                    if fp.exists():
                        if not book.cover:
                            from django.core.files.base import File
                            with open(fp, 'rb') as f:
                                book.cover.save(f"images/books/{fp.name}", File(f), save=True)
                        break
            except Exception:
                # Non-fatal: skip attaching covers if anything goes wrong
                pass

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(DATASET)} books (created: {created_books})."))
