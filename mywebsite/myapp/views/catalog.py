from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count
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

    books = (
        Book.objects.all()
        .prefetch_related("authors", "tags")
        .select_related("category")
        .annotate(available_count=Count("copies", filter=Q(copies__status=BookCopy.STATUS_AVAILABLE)))
    )
    if query:
        alt_query = query.replace('/', ' ').replace('_', ' ')
        books = books.filter(
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
            books = books.filter(category_id__in=ids)

    selected_tag = None
    if tag_slug:
        selected_tag = Tag.objects.filter(slug=tag_slug).first()
        if selected_tag:
            books = books.filter(tags=selected_tag)

    top_categories = (
        Category.objects.filter(Q(parent__isnull=True) | Q(books__isnull=False))
        .distinct()
        .order_by("name")
    )
    popular_tags = Tag.objects.order_by("name")[:20]

    # Fuzzy suggestions when no results
    did_you_mean = []
    if query and not books.exists():
        titles = list(Book.objects.values_list("title", flat=True))
        did_you_mean = difflib.get_close_matches(query, titles, n=5, cutoff=0.6)

    # Suggestions for the search box (no extra endpoint):
    all_categories = Category.objects.order_by("name").only("name")
    sample_titles = Book.objects.order_by("-id").values_list("title", flat=True)[:50]

    context = {
        "books": books,
        "search_query": query,
        "top_categories": top_categories,
        "selected_category": selected_category,
        "selected_tag": selected_tag,
        "popular_tags": popular_tags,
        "all_categories": all_categories,
        "sample_titles": sample_titles,
        "did_you_mean": did_you_mean,
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
        # If still small, add fuzzy close matches
        if len(suggestions) < 10:
            all_titles = list(Book.objects.values_list("title", flat=True))
            fuzzy = difflib.get_close_matches(q, all_titles, n=10, cutoff=0.6)
            for s in fuzzy:
                if s not in suggestions:
                    suggestions.append(s)
                if len(suggestions) >= 10:
                    break
    return JsonResponse({"suggestions": list(suggestions)})
