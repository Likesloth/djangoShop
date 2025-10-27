from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify

from myapp.models import Author, Book, BookCopy, Loan, Category, Tag


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
        # Categories
        cat_science, _ = Category.objects.get_or_create(name="Science", slug="science", parent=None)
        cat_cs, _ = Category.objects.get_or_create(name="Computer Science", slug="computer-science", parent=cat_science)
        cat_se, _ = Category.objects.get_or_create(name="Software Engineering", slug="software-engineering", parent=cat_cs)

        # Tags
        tag_machine_learning, _ = Tag.objects.get_or_create(name="machine-learning", slug="machine-learning")
        tag_design_patterns, _ = Tag.objects.get_or_create(name="design-patterns", slug="design-patterns")
        tag_classic, _ = Tag.objects.get_or_create(name="classic", slug="classic")

        b1, _ = Book.objects.get_or_create(
            isbn13="9780099448761",
            defaults={"title": "Norwegian Wood", "language": "EN", "publish_year": 1987},
        )
        b1.authors.add(murakami)
        b1.category = cat_science
        b1.save(update_fields=["category"])
        b1.tags.add(tag_classic)

        b2, _ = Book.objects.get_or_create(
            isbn13="9780141036144",
            defaults={"title": "1984", "language": "EN", "publish_year": 1949},
        )
        b2.authors.add(orwell)
        b2.category = cat_cs
        b2.save(update_fields=["category"])
        b2.tags.add(tag_classic)

        b3, _ = Book.objects.get_or_create(
            isbn13="9781503290563",
            defaults={"title": "Pride and Prejudice", "language": "EN", "publish_year": 1813},
        )
        b3.authors.add(austen)
        b3.category = cat_se
        b3.save(update_fields=["category"])
        b3.tags.add(tag_design_patterns)

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

        # Additional 20 technical books with categories/tags and one copy each
        extra_books = [
            {"isbn13": "9780132350884", "title": "Clean Code", "authors": ["Robert C. Martin"], "language": "EN", "publish_year": 2008, "tags": ["clean-code", "software-engineering", "best-practices"]},
            {"isbn13": "9780201616224", "title": "The Pragmatic Programmer", "authors": ["Andrew Hunt", "David Thomas"], "language": "EN", "publish_year": 1999, "tags": ["software-engineering", "pragmatic", "career"]},
            {"isbn13": "9780201633610", "title": "Design Patterns", "authors": ["Erich Gamma", "Richard Helm", "Ralph Johnson", "John Vlissides"], "language": "EN", "publish_year": 1994, "tags": ["design-patterns", "oop"]},
            {"isbn13": "9780134757599", "title": "Refactoring (2nd Edition)", "authors": ["Martin Fowler"], "language": "EN", "publish_year": 2018, "tags": ["refactoring", "clean-code"]},
            {"isbn13": "9780262033848", "title": "Introduction to Algorithms", "authors": ["Thomas H. Cormen", "Charles E. Leiserson", "Ronald L. Rivest", "Clifford Stein"], "language": "EN", "publish_year": 2009, "tags": ["algorithms", "data-structures"]},
            {"isbn13": "9780262510875", "title": "Structure and Interpretation of Computer Programs", "authors": ["Harold Abelson", "Gerald Jay Sussman", "Julie Sussman"], "language": "EN", "publish_year": 1996, "tags": ["programming", "computer-science"]},
            {"isbn13": "9780136042594", "title": "Artificial Intelligence: A Modern Approach", "authors": ["Stuart Russell", "Peter Norvig"], "language": "EN", "publish_year": 2010, "tags": ["ai", "artificial-intelligence"]},
            {"isbn13": "9780262035613", "title": "Deep Learning", "authors": ["Ian Goodfellow", "Yoshua Bengio", "Aaron Courville"], "language": "EN", "publish_year": 2016, "tags": ["machine-learning", "deep-learning"]},
            {"isbn13": "9780387310732", "title": "Pattern Recognition and Machine Learning", "authors": ["Christopher M. Bishop"], "language": "EN", "publish_year": 2006, "tags": ["machine-learning", "statistics"]},
            {"isbn13": "9781593276034", "title": "Python Crash Course", "authors": ["Eric Matthes"], "language": "EN", "publish_year": 2015, "tags": ["python", "beginners"]},
            {"isbn13": "9781491946008", "title": "Fluent Python", "authors": ["Luciano Ramalho"], "language": "EN", "publish_year": 2015, "tags": ["python", "advanced"]},
            {"isbn13": "9780134685991", "title": "Effective Java", "authors": ["Joshua Bloch"], "language": "EN", "publish_year": 2018, "tags": ["java", "best-practices"]},
            {"isbn13": "9781492078005", "title": "Head First Design Patterns (2nd Edition)", "authors": ["Eric Freeman", "Elisabeth Robson"], "language": "EN", "publish_year": 2020, "tags": ["design-patterns", "oop"]},
            {"isbn13": "9780134494166", "title": "Clean Architecture", "authors": ["Robert C. Martin"], "language": "EN", "publish_year": 2017, "tags": ["architecture", "clean-code"]},
            {"isbn13": "9780321125217", "title": "Domain-Driven Design", "authors": ["Eric Evans"], "language": "EN", "publish_year": 2003, "tags": ["ddd", "architecture"]},
            {"isbn13": "9780321601919", "title": "Continuous Delivery", "authors": ["Jez Humble", "David Farley"], "language": "EN", "publish_year": 2010, "tags": ["devops", "ci-cd"]},
            {"isbn13": "9780201835953", "title": "The Mythical Man-Month", "authors": ["Frederick P. Brooks Jr."], "language": "EN", "publish_year": 1975, "tags": ["project-management", "history"]},
            {"isbn13": "9780131177055", "title": "Working Effectively with Legacy Code", "authors": ["Michael Feathers"], "language": "EN", "publish_year": 2004, "tags": ["legacy-code", "testing"]},
            {"isbn13": "9780984782857", "title": "Cracking the Coding Interview", "authors": ["Gayle Laakmann McDowell"], "language": "EN", "publish_year": 2015, "tags": ["interview", "algorithms"]},
            {"isbn13": "9780137081073", "title": "The Clean Coder", "authors": ["Robert C. Martin"], "language": "EN", "publish_year": 2011, "tags": ["professionalism", "clean-code"]},
        ]

        # Assign everything under Software Engineering tree for simplicity
        se_category = Category.objects.get(slug="software-engineering")

        for item in extra_books:
            book, created = Book.objects.get_or_create(
                isbn13=item["isbn13"],
                defaults={
                    "title": item["title"],
                    "language": item.get("language") or "EN",
                    "publish_year": item.get("publish_year"),
                    "category": se_category,
                },
            )
            # Authors
            for full_name in item.get("authors", []):
                a, _ = Author.objects.get_or_create(full_name=full_name)
                book.authors.add(a)
            # Category (set if not defaulted during creation)
            if not book.category_id:
                book.category = se_category
                book.save(update_fields=["category"])
            # Tags
            for t in item.get("tags", []):
                tag, _ = Tag.objects.get_or_create(name=t, slug=slugify(t))
                book.tags.add(tag)
            # Copies
            base = slugify(book.title)[:8].upper()
            barcode = f"BC-{base}-001"
            BookCopy.objects.get_or_create(
                barcode=barcode,
                defaults={"book": book, "location": "Main", "status": BookCopy.STATUS_AVAILABLE},
            )

        self.stdout.write(self.style.SUCCESS("Added 20 technical books with tags under Software Engineering."))

        # Helper to create/find a hierarchical category path
        def ensure_category(path_list):
            parent = None
            for name in path_list:
                obj, _ = Category.objects.get_or_create(
                    name=name,
                    slug=slugify(name),
                    parent=parent,
                )
                parent = obj
            return parent

        # Additional books across other domains (non-CS)
        general_books = [
            {"isbn13": "9780743273565", "title": "The Great Gatsby", "authors": ["F. Scott Fitzgerald"], "language": "EN", "publish_year": 1925, "category_path": ["Literature"], "tags": ["classic", "novel"]},
            {"isbn13": "9780061120084", "title": "To Kill a Mockingbird", "authors": ["Harper Lee"], "language": "EN", "publish_year": 1960, "category_path": ["Literature"], "tags": ["classic", "novel"]},
            {"isbn13": "9780062316097", "title": "Sapiens", "authors": ["Yuval Noah Harari"], "language": "EN", "publish_year": 2011, "category_path": ["History"], "tags": ["history", "anthropology"]},
            {"isbn13": "9780399590504", "title": "Educated", "authors": ["Tara Westover"], "language": "EN", "publish_year": 2018, "category_path": ["History"], "tags": ["memoir"]},
            {"isbn13": "9780374533557", "title": "Thinking, Fast and Slow", "authors": ["Daniel Kahneman"], "language": "EN", "publish_year": 2011, "category_path": ["Psychology"], "tags": ["behavioral", "decision-making"]},
            {"isbn13": "9780735211292", "title": "Atomic Habits", "authors": ["James Clear"], "language": "EN", "publish_year": 2018, "category_path": ["Business"], "tags": ["self-help", "productivity"]},
            {"isbn13": "9780307887894", "title": "The Lean Startup", "authors": ["Eric Ries"], "language": "EN", "publish_year": 2011, "category_path": ["Business"], "tags": ["startup", "entrepreneurship"]},
            {"isbn13": "9780804139298", "title": "Zero to One", "authors": ["Peter Thiel", "Blake Masters"], "language": "EN", "publish_year": 2014, "category_path": ["Business"], "tags": ["startup", "innovation"]},
            {"isbn13": "9781599869773", "title": "The Art of War", "authors": ["Sun Tzu"], "language": "EN", "publish_year": 5, "category_path": ["Philosophy"], "tags": ["strategy", "classic"]},
            {"isbn13": "9780812968255", "title": "Meditations", "authors": ["Marcus Aurelius"], "language": "EN", "publish_year": 180, "category_path": ["Philosophy"], "tags": ["stoicism", "classic"]},
            {"isbn13": "9780553380163", "title": "A Brief History of Time", "authors": ["Stephen Hawking"], "language": "EN", "publish_year": 1988, "category_path": ["Science", "Physics"], "tags": ["physics", "cosmology"]},
            {"isbn13": "9780199291151", "title": "The Selfish Gene", "authors": ["Richard Dawkins"], "language": "EN", "publish_year": 1976, "category_path": ["Science", "Biology"], "tags": ["evolution", "biology"]},
            {"isbn13": "9781476763491", "title": "The Man Who Knew Infinity", "authors": ["Robert Kanigel"], "language": "EN", "publish_year": 1991, "category_path": ["Science", "Mathematics"], "tags": ["mathematics", "biography"]},
            {"isbn13": "9780205309023", "title": "The Elements of Style", "authors": ["William Strunk Jr.", "E. B. White"], "language": "EN", "publish_year": 1999, "category_path": ["Literature"], "tags": ["writing", "style"]},
            {"isbn13": "9780465050659", "title": "The Design of Everyday Things", "authors": ["Don Norman"], "language": "EN", "publish_year": 2013, "category_path": ["Arts"], "tags": ["design", "ux"]},
            {"isbn13": "9781936891023", "title": "The War of Art", "authors": ["Steven Pressfield"], "language": "EN", "publish_year": 2002, "category_path": ["Arts"], "tags": ["creativity", "mindset"]},
            {"isbn13": "9781501111104", "title": "Grit", "authors": ["Angela Duckworth"], "language": "EN", "publish_year": 2016, "category_path": ["Psychology"], "tags": ["motivation", "success"]},
            {"isbn13": "9780060731335", "title": "Freakonomics", "authors": ["Steven D. Levitt", "Stephen J. Dubner"], "language": "EN", "publish_year": 2005, "category_path": ["Economics"], "tags": ["economics", "pop-science"]},
            {"isbn13": "9781594204111", "title": "The Signal and the Noise", "authors": ["Nate Silver"], "language": "EN", "publish_year": 2012, "category_path": ["Science", "Mathematics"], "tags": ["statistics", "prediction"]},
            {"isbn13": "9780812981605", "title": "The Power of Habit", "authors": ["Charles Duhigg"], "language": "EN", "publish_year": 2012, "category_path": ["Psychology"], "tags": ["habits", "behavior"]},
        ]

        for item in general_books:
            cat = ensure_category(item.get("category_path", ["General"]))
            book, created = Book.objects.get_or_create(
                isbn13=item["isbn13"],
                defaults={
                    "title": item["title"],
                    "language": item.get("language") or "EN",
                    "publish_year": item.get("publish_year"),
                    "category": cat,
                },
            )
            for full_name in item.get("authors", []):
                a, _ = Author.objects.get_or_create(full_name=full_name)
                book.authors.add(a)
            if not book.category_id:
                book.category = cat
                book.save(update_fields=["category"])
            for t in item.get("tags", []):
                tag, _ = Tag.objects.get_or_create(name=t, slug=slugify(t))
                book.tags.add(tag)
            base = slugify(book.title)[:8].upper()
            barcode = f"BC-{base}-001"
            BookCopy.objects.get_or_create(
                barcode=barcode,
                defaults={"book": book, "location": "Main", "status": BookCopy.STATUS_AVAILABLE},
            )

        self.stdout.write(self.style.SUCCESS("Added 20 general books across multiple categories."))
