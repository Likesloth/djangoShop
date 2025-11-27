"""
Management command to set up and manage the database cache table.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Set up the database cache table and optionally warm up cache entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all cache entries',
        )
        parser.add_argument(
            '--warm',
            action='store_true',
            help='Warm up common cache entries',
        )

    def handle(self, *args, **options):
        # Create cache table if it doesn't exist
        self.stdout.write('Creating cache table...')
        try:
            call_command('createcachetable')
            self.stdout.write(self.style.SUCCESS('✓ Cache table created/verified'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Cache table may already exist: {e}'))

        if options['clear']:
            self.stdout.write('Clearing all cache...')
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ Cache cleared'))

        if options['warm']:
            self.stdout.write('Warming up cache...')
            self._warm_cache()
            self.stdout.write(self.style.SUCCESS('✓ Cache warmed up'))

        self.stdout.write(self.style.SUCCESS('\n✓ Cache setup complete!'))

    def _warm_cache(self):
        """Pre-populate common cache entries"""
        from django.db import models
        from myapp.models import Category, Tag, Book

        # Warm up catalog page cache entries
        self.stdout.write('  - Caching categories...')
        top_categories = list(
            Category.objects.filter(
                models.Q(parent__isnull=True) | models.Q(books__isnull=False)
            )
            .distinct()
            .order_by("name")
        )
        cache.set('catalog_top_categories', top_categories, 1800)

        self.stdout.write('  - Caching tags...')
        popular_tags = list(Tag.objects.order_by("name")[:20])
        cache.set('catalog_popular_tags', popular_tags, 1800)

        self.stdout.write('  - Caching sample data...')
        all_categories = list(Category.objects.order_by("name").only("name"))
        cache.set('catalog_all_categories', all_categories, 1800)

        sample_titles = list(Book.objects.order_by("-id").values_list("title", flat=True)[:50])
        cache.set('catalog_sample_titles', sample_titles, 1800)

        recent_titles = list(Book.objects.order_by('-id').values_list("title", flat=True)[:500])
        cache.set('catalog_recent_titles', recent_titles, 3600)
