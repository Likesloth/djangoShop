from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import connection
from django.test.utils import override_settings
from django.urls import reverse
import time

from .models import Book, Author, Category, Tag, BookCopy


class PerformanceTests(TestCase):
    """
    Performance tests for catalog and caching system.
    These tests verify that optimizations are working correctly.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create test data once for all tests in this class"""
        # Create test user
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create categories
        cls.category1 = Category.objects.create(name='Computer Science', slug='computer-science')
        cls.category2 = Category.objects.create(name='Fiction', slug='fiction')
        
        # Create tags
        cls.tag1 = Tag.objects.create(name='textbook', slug='textbook')
        cls.tag2 = Tag.objects.create(name='beginner', slug='beginner')
        
        # Create authors
        cls.author1 = Author.objects.create(full_name='John Doe')
        cls.author2 = Author.objects.create(full_name='Jane Smith')
        
        # Create books (50 books for realistic testing)
        cls.books = []
        for i in range(50):
            book = Book.objects.create(
                isbn13=f'978000000000{i:02d}',
                title=f'Test Book {i}',
                language='EN',
                publish_year=2020 + (i % 5),
                category=cls.category1 if i % 2 == 0 else cls.category2
            )
            book.authors.add(cls.author1 if i % 2 == 0 else cls.author2)
            book.tags.add(cls.tag1 if i % 3 == 0 else cls.tag2)
            
            # Create copies for each book
            for j in range(3):
                BookCopy.objects.create(
                    book=book,
                    barcode=f'BC-{i:02d}-{j}',
                    location=f'Shelf-{i}',
                    status=BookCopy.STATUS_AVAILABLE if j < 2 else BookCopy.STATUS_ON_LOAN
                )
            cls.books.append(book)
    
    def setUp(self):
        """Clear cache before each test"""
        cache.clear()
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_cache_is_working(self):
        """Verify that Django cache is functioning"""
        # Set a cache value
        cache.set('test_key', 'test_value', 30)
        
        # Retrieve it
        value = cache.get('test_key')
        
        self.assertEqual(value, 'test_value', "Cache should store and retrieve values")
        
        # Clear and verify it's gone
        cache.delete('test_key')
        value = cache.get('test_key')
        
        self.assertIsNone(value, "Cache should return None for deleted keys")
    
    def test_catalog_caching_effectiveness(self):
        """Test that catalog list caches expensive queries"""
        # First request - should populate cache
        response1 = self.client.get(reverse('catalog-list'))
        
        # Verify cache keys exist after first request
        top_categories = cache.get('catalog_top_categories')
        popular_tags = cache.get('catalog_popular_tags')
        
        self.assertIsNotNone(top_categories, "Top categories should be cached")
        self.assertIsNotNone(popular_tags, "Popular tags should be cached")
        
        # Second request - should use cache
        response2 = self.client.get(reverse('catalog-list'))
        
        # Both responses should be successful
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
    
    def test_catalog_list_query_count(self):
        """Verify that catalog list uses optimized queries with prefetch/select_related"""
        # Track number of database queries
        with self.assertNumQueries(8):  # Should be reasonable number, not N+1
            response = self.client.get(reverse('catalog-list'))
            
            # Access the books in the template context to trigger queries
            books = response.context['books']
            for book in books:
                # These should not trigger additional queries due to prefetch_related
                _ = list(book.authors.all())
                _ = list(book.tags.all())
                _ = book.category
    
    def test_search_performance(self):
        """Test search functionality performance"""
        start_time = time.time()
        
        # Search by title
        response = self.client.get(reverse('catalog-list'), {'q': 'Test Book'})
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # Search should complete in under 1 second even with 50 books
        self.assertLess(duration, 1.0, f"Search took {duration:.3f}s, should be < 1s")
    
    def test_category_filter_uses_descendants(self):
        """Test that category filtering includes subcategories"""
        # Create a parent-child category relationship
        parent = Category.objects.create(name='Science', slug='science')
        child = Category.objects.create(
            name='Physics', 
            slug='physics', 
            parent=parent
        )
        
        # Create a book in the child category
        book_in_child = Book.objects.create(
            isbn13='9780000000099',
            title='Physics Book',
            language='EN',
            category=child
        )
        
        # Filter by parent category
        response = self.client.get(reverse('catalog-list'), {'category': 'science'})
        
        self.assertEqual(response.status_code, 200)
        # The book from the child category should appear when filtering by parent
        book_titles = [b.title for b in response.context['books']]
        self.assertIn('Physics Book', book_titles, 
                     "Books from subcategories should appear when filtering by parent category")
    
    def test_pagination_performance(self):
        """Test that pagination doesn't load all books"""
        # Request page 1
        response = self.client.get(reverse('catalog-list'), {'page': '1'})
        
        self.assertEqual(response.status_code, 200)
        
        # Should show 12 books per page (as configured)
        books = response.context['books']
        self.assertLessEqual(len(books), 12, "Should not load more than 12 books per page")
        
        # Verify pagination object exists
        self.assertTrue(books.has_other_pages(), "Should have pagination with 50 books")
    
    def test_suggest_titles_caching(self):
        """Test that title suggestions are cached"""
        # First request
        response1 = self.client.get(reverse('suggest-titles'), {'q': 'Test'})
        self.assertEqual(response1.status_code, 200)
        
        # The view uses @cache_page decorator, so identical requests should be cached
        start_time = time.time()
        response2 = self.client.get(reverse('suggest-titles'), {'q': 'Test'})
        duration = time.time() - start_time
        
        self.assertEqual(response2.status_code, 200)
        # Cached response should be very fast (< 10ms typically)
        self.assertLess(duration, 0.1, "Cached suggestion should be fast")
    
    def test_book_detail_query_optimization(self):
        """Test that book detail page uses select_related for copies"""
        book = self.books[0]
        
        # Should use select_related to minimize queries
        with self.assertNumQueries(4):  # Should be low, not N+1
            response = self.client.get(reverse('catalog-detail', args=[book.id]))
            
            self.assertEqual(response.status_code, 200)
            
            # Access copies to trigger queries
            copies = response.context['copies']
            for copy in copies:
                _ = copy.book  # Should not trigger query due to select_related
    
    def test_availability_count_annotation(self):
        """Test that availability count uses database aggregation not Python"""
        # Get catalog page
        response = self.client.get(reverse('catalog-list'))
        
        books = response.context['books']
        
        # Each book should have available_count from annotation
        for book in books:
            # This should be calculated in the database, not Python
            self.assertTrue(hasattr(book, 'available_count'), 
                          "Books should have available_count annotation")
            self.assertIsInstance(book.available_count, int)
    
    def test_did_you_mean_suggestions(self):
        """Test fuzzy matching for search suggestions"""
        # Search for something that doesn't exist but is close
        response = self.client.get(reverse('catalog-list'), {'q': 'Tset Bok'})
        
        self.assertEqual(response.status_code, 200)
        
        # Should show "did you mean" suggestions
        did_you_mean = response.context.get('did_you_mean', [])
        
        # With books titled "Test Book X", fuzzy matching should find them
        self.assertGreater(len(did_you_mean), 0, 
                          "Should suggest similar titles when search has no results")
    
    def test_view_mode_toggle(self):
        """Test that view mode parameter works"""
        # Test list view (default)
        response_list = self.client.get(reverse('catalog-list'), {'view': 'list'})
        self.assertEqual(response_list.status_code, 200)
        self.assertEqual(response_list.context['view_mode'], 'list')
        
        # Test grid view
        response_grid = self.client.get(reverse('catalog-list'), {'view': 'grid'})
        self.assertEqual(response_grid.status_code, 200)
        self.assertEqual(response_grid.context['view_mode'], 'grid')
        
        # Test invalid view defaults to list
        response_invalid = self.client.get(reverse('catalog-list'), {'view': 'invalid'})
        self.assertEqual(response_invalid.status_code, 200)
        self.assertEqual(response_invalid.context['view_mode'], 'list')


class CatalogFunctionalTests(TestCase):
    """Functional tests for catalog features"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        # Create test data
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.tag = Tag.objects.create(name='test-tag', slug='test-tag')
        self.author = Author.objects.create(full_name='Test Author')
        
        self.book = Book.objects.create(
            isbn13='9780000000001',
            title='Test Book',
            language='EN',
            publish_year=2024,
            category=self.category
        )
        self.book.authors.add(self.author)
        self.book.tags.add(self.tag)
        
        BookCopy.objects.create(
            book=self.book,
            barcode='TEST-001',
            location='Test Shelf',
            status=BookCopy.STATUS_AVAILABLE
        )
    
    def test_catalog_list_loads(self):
        """Test that catalog list page loads successfully"""
        response = self.client.get(reverse('catalog-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
    
    def test_book_detail_loads(self):
        """Test that book detail page loads successfully"""
        response = self.client.get(reverse('catalog-detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'TEST-001')  # Barcode should appear
    
    def test_category_filter(self):
        """Test filtering by category"""
        response = self.client.get(reverse('catalog-list'), {'category': 'test-category'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_category'], self.category)
    
    def test_tag_filter(self):
        """Test filtering by tag"""
        response = self.client.get(reverse('catalog-list'), {'tag': 'test-tag'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tag'], self.tag)
    
    def test_search_by_title(self):
        """Test searching by book title"""
        response = self.client.get(reverse('catalog-list'), {'q': 'Test Book'})
        self.assertEqual(response.status_code, 200)
        books = list(response.context['books'])
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, 'Test Book')
    
    def test_search_by_isbn(self):
        """Test searching by ISBN"""
        response = self.client.get(reverse('catalog-list'), {'q': '9780000000001'})
        self.assertEqual(response.status_code, 200)
        books = list(response.context['books'])
        self.assertEqual(len(books), 1)
    
    def test_search_by_author(self):
        """Test searching by author name"""
        response = self.client.get(reverse('catalog-list'), {'q': 'Test Author'})
        self.assertEqual(response.status_code, 200)
        books = list(response.context['books'])
        self.assertEqual(len(books), 1)
