from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count

from ..models import Book, BookCopy


def catalog_list(request):
    query = (request.GET.get("q") or "").strip()
    books = (
        Book.objects.all()
        .prefetch_related("authors")
        .annotate(available_count=Count("copies", filter=Q(copies__status=BookCopy.STATUS_AVAILABLE)))
    )
    if query:
        books = books.filter(Q(title__icontains=query) | Q(isbn13__icontains=query))
    context = {"books": books, "search_query": query}
    return render(request, "myapp/catalog/catalog_list.html", context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    copies = book.copies.select_related().all()
    available_count = copies.filter(status=BookCopy.STATUS_AVAILABLE).count()
    context = {"book": book, "copies": copies, "available_count": available_count}
    return render(request, "myapp/catalog/book_detail.html", context)

