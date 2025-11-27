from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import difflib

from ..models import Book, BookCopy, Category, Tag


def _descendant_ids(category: Category):
    if not category:
        return []
    ids = [category.id]
    frontier = [category.id]
    while frontier:
        children = list(Category.objects.filter(parent_id__in=frontier).values_list("id", flat=True))
        new = [c for c in children if c not in ids]
        ids.extend(new)
        frontier = new
    return ids


def catalog_list(request):
    query = (request.GET.get("q") or "").strip()
    cat_slug = (request.GET.get("category") or "").strip()
    tag_slug = (request.GET.get("tag") or "").strip()
    # view mode toggle: 'list' (default) or 'grid'
    view_mode = (request.GET.get("view") or "list").strip().lower()
    if view_mode not in ("list", "grid"):
        view_mode = "list"

    books_qs = (
        Book.objects.all()
        .prefetch_related("authors", "tags")
        .select_related("category")
        .annotate(available_count=Count("copies", filter=Q(copies__status=BookCopy.STATUS_AVAILABLE)))
    )
    if query:
        alt_query = query.replace('/', ' ').replace('_', ' ')
        books_qs = books_qs.filter(
            Q(title__icontains=query)
            | Q(isbn13__icontains=query)
            | Q(authors__full_name__icontains=query)
            | Q(tags__name__icontains=query)
            | Q(category__name__icontains=query)
            | Q(category__parent__name__icontains=query)
            | Q(category__name__icontains=alt_query)
            | Q(category__parent__name__icontains=alt_query)
            | Q(tags__name__icontains=alt_query)
        ).distinct()

    selected_category = None
    if cat_slug:
        selected_category = Category.objects.filter(slug=cat_slug).first()
        if selected_category:
            ids = _descendant_ids(selected_category)
            books_qs = books_qs.filter(category_id__in=ids)

    selected_tag = None
    if tag_slug:
        selected_tag = Tag.objects.filter(slug=tag_slug).first()
        if selected_tag:
            books_qs = books_qs.filter(tags=selected_tag)

    # Cache category and tag lists (they don't change often)
    top_categories = cache.get('catalog_top_categories')
    if top_categories is None:
        top_categories = list(
            Category.objects.filter(Q(parent__isnull=True) | Q(books__isnull=False))
            .distinct()
            .order_by("name")
        )
        cache.set('catalog_top_categories', top_categories, 1800)  # Cache for 30 min
    
    popular_tags = cache.get('catalog_popular_tags')
    if popular_tags is None:
        popular_tags = list(Tag.objects.order_by("name")[:20])
        cache.set('catalog_popular_tags', popular_tags, 1800)  # Cache for 30 min

    # Optimized fuzzy suggestions - only use recent books (top 500) instead of ALL
    did_you_mean = []
    if query and not books_qs.exists():
        recent_titles = cache.get('catalog_recent_titles')
        if recent_titles is None:
            recent_titles = list(Book.objects.order_by('-id').values_list("title", flat=True)[:500])
            cache.set('catalog_recent_titles', recent_titles, 3600)  # Cache for 1 hour
        did_you_mean = difflib.get_close_matches(query, recent_titles, n=5, cutoff=0.6)

    # Suggestions for the search box
    all_categories = cache.get('catalog_all_categories')
    if all_categories is None:
        all_categories = list(Category.objects.order_by("name").only("name"))
        cache.set('catalog_all_categories', all_categories, 1800)  # Cache for 30 min
    
    sample_titles = cache.get('catalog_sample_titles')
    if sample_titles is None:
        sample_titles = list(Book.objects.order_by("-id").values_list("title", flat=True)[:50])
        cache.set('catalog_sample_titles', sample_titles, 1800)  # Cache for 30 min

    # Pagination (works for both grid and list views)
    paginator = Paginator(books_qs.order_by("-id"), 12)
    page_number = request.GET.get("page")
    books_page = paginator.get_page(page_number)

    context = {
        "books": books_page,
        "search_query": query,
        "top_categories": top_categories,
        "selected_category": selected_category,
        "selected_tag": selected_tag,
        "popular_tags": popular_tags,
        "all_categories": all_categories,
        "sample_titles": sample_titles,
        "did_you_mean": did_you_mean,
        "view_mode": view_mode,
    }
    return render(request, "myapp/catalog/catalog_list.html", context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    copies = book.copies.select_related().all()
    available_count = copies.filter(status=BookCopy.STATUS_AVAILABLE).count()
    context = {
        "book": book,
        "copies": copies,
        "available_count": available_count,
    }
    return render(request, "myapp/catalog/book_detail.html", context)


@cache_page(3600)  # Cache for 1 hour
def suggest_titles(request):
    """Return up to 10 title suggestions for the given query (prefix then contains)."""
    q = (request.GET.get("q") or "").strip()
    suggestions = []
    if q:
        # Prefer prefix matches
        prefix_qs = Book.objects.filter(title__istartswith=q).values_list("title", flat=True)[:10]
        suggestions.extend(prefix_qs)
        if len(suggestions) < 10:
            extra = (
                Book.objects.filter(title__icontains=q)
                .exclude(title__in=suggestions)
                .values_list("title", flat=True)[: (10 - len(suggestions))]
            )
            suggestions.extend(extra)
        # Optimized fuzzy matching - only use top 1000 recent books instead of ALL
        if len(suggestions) < 10:
            # Try to get from cache first
            cache_key = f'suggest_fuzzy_{q[:20]}'  # Limit cache key length
            fuzzy = cache.get(cache_key)
            if fuzzy is None:
                recent_titles = list(Book.objects.order_by('-id').values_list("title", flat=True)[:1000])
                fuzzy = difflib.get_close_matches(q, recent_titles, n=10, cutoff=0.6)
                cache.set(cache_key, fuzzy, 3600)  # Cache for 1 hour
            
            for s in fuzzy:
                if s not in suggestions:
                    suggestions.append(s)
                if len(suggestions) >= 10:
                    break
    return JsonResponse({"suggestions": list(suggestions)})
