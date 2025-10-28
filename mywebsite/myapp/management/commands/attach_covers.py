from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files.base import File
from django.conf import settings

from ...models import Book


class Command(BaseCommand):
    help = "Attach cover images to books if media/images/books/<isbn13>.(jpg|jpeg|png|webp) exists and cover is empty."

    def handle(self, *args, **options):
        covers_dir = Path(settings.MEDIA_ROOT) / 'images' / 'books'
        if not covers_dir.exists():
            self.stdout.write(self.style.WARNING(f"Covers directory not found: {covers_dir}"))
            return

        updated = 0
        skipped = 0
        for book in Book.objects.all():
            if book.cover:
                skipped += 1
                continue
            match = None
            for ext in ('.jpg', '.jpeg', '.png', '.webp'):
                fp = covers_dir / f"{book.isbn13}{ext}"
                if fp.exists():
                    match = fp
                    break
            if not match:
                continue
            with open(match, 'rb') as f:
                book.cover.save(f"images/books/{match.name}", File(f), save=True)
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Attached covers: {updated}; already had cover: {skipped}."))

