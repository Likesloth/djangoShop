from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count

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
        books = books.filter(
            Q(title__icontains=query)
            | Q(isbn13__icontains=query)
            | Q(authors__full_name__icontains=query)
            | Q(tags__name__icontains=query)
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

    context = {
        "books": books,
        "search_query": query,
        "top_categories": top_categories,
        "selected_category": selected_category,
        "selected_tag": selected_tag,
        "popular_tags": popular_tags,
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
