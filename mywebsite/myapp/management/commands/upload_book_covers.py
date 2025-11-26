"""
Django management command to bulk upload book covers to Cloudinary.

Usage:
    1. Put all book cover images in a folder (e.g., book_covers/)
    2. Name images by ISBN13 (e.g., 9780547928227.jpg, 9780123456789.png)
    3. Run: python manage.py upload_book_covers /path/to/book_covers/

The command will:
- Find all images in the folder
- Match them to books by ISBN13
- Upload to Cloudinary automatically
- Show progress and results
"""

from django.core.management.base import BaseCommand
from django.core.files import File
from myapp.models import Book
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Bulk upload book covers from a directory. Images should be named by ISBN13.'

    def add_arguments(self, parser):
        parser.add_argument(
            'folder',
            type=str,
            help='Path to folder containing book cover images (named by ISBN13)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing book covers'
        )

    def handle(self, *args, **options):
        folder_path = Path(options['folder'])
        dry_run = options['dry_run']
        overwrite = options['overwrite']

        if not folder_path.exists():
            self.stdout.write(self.style.ERROR(f'Folder not found: {folder_path}'))
            return

        if not folder_path.is_dir():
            self.stdout.write(self.style.ERROR(f'Not a directory: {folder_path}'))
            return

        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

        # Find all image files
        image_files = [
            f for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        if not image_files:
            self.stdout.write(self.style.WARNING(f'No image files found in {folder_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'\nFound {len(image_files)} image file(s) in {folder_path}\n'))

        # Track statistics
        uploaded = 0
        skipped = 0
        errors = 0
        not_found = 0

        # Process each image
        for image_file in sorted(image_files):
            # Extract ISBN from filename (without extension)
            isbn13 = image_file.stem
            
            # Clean ISBN (remove hyphens, spaces)
            isbn13_clean = isbn13.replace('-', '').replace(' ', '')

            # Try to find book by ISBN
            try:
                book = Book.objects.get(isbn13=isbn13_clean)
            except Book.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Book not found for ISBN: {isbn13} ({image_file.name})')
                )
                not_found += 1
                continue

            # Check if book already has a cover
            if book.cover and not overwrite:
                self.stdout.write(
                    self.style.WARNING(f'  ⊘ Skipping {book.title} - already has cover (use --overwrite to replace)')
                )
                skipped += 1
                continue

            # Dry run - show what would be uploaded
            if dry_run:
                action = "REPLACE" if book.cover else "ADD"
                self.stdout.write(
                    self.style.NOTICE(f'  [DRY RUN] Would {action} cover for: {book.title} ({isbn13_clean})')
                )
                uploaded += 1
                continue

            # Actually upload the cover
            try:
                with open(image_file, 'rb') as f:
                    book.cover.save(image_file.name, File(f), save=True)
                
                action = "Replaced" if overwrite else "Added"
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {action} cover for: {book.title} ({isbn13_clean})')
                )
                uploaded += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error uploading {image_file.name}: {str(e)}')
                )
                errors += 1

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\nSUMMARY:'))
        self.stdout.write('='*60)
        
        if dry_run:
            self.stdout.write(f'  Would upload: {uploaded}')
        else:
            self.stdout.write(f'  ✓ Uploaded: {uploaded}')
        
        if skipped > 0:
            self.stdout.write(f'  ⊘ Skipped (already have covers): {skipped}')
        if not_found > 0:
            self.stdout.write(f'  ⚠ Not found (no matching ISBN): {not_found}')
        if errors > 0:
            self.stdout.write(f'  ✗ Errors: {errors}')
        
        self.stdout.write('='*60 + '\n')

        if dry_run:
            self.stdout.write(self.style.NOTICE('\nThis was a dry run. Run without --dry-run to actually upload.\n'))
        elif uploaded > 0:
            self.stdout.write(self.style.SUCCESS('\n🎉 Done! All covers uploaded to Cloudinary!\n'))
