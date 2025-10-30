from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q, Count
import difflib

from ..models import Product, Book, BookCopy, Category, Tag


def home(request):
    all_products = Product.objects.all().order_by('-id')
    paginator = Paginator(all_products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "myapp/pages/home.html", {"allproduct": page_obj})


def _descendant_ids(category):
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


def library_home(request):
    query = (request.GET.get("q") or "").strip()
    cat_slug = (request.GET.get("category") or "").strip()
    tag_slug = (request.GET.get("tag") or "").strip()

    books_qs = (
        Book.objects.all()
        .prefetch_related("authors", "tags")
        .select_related("category")
        .annotate(available_count=Count("copies", filter=Q(copies__status=BookCopy.STATUS_AVAILABLE)))
        .order_by("-id")
    )
    if query:
        # Also search by category name (and parent name) and be tolerant to separators like '/'
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

    # Fuzzy suggestions when no results
    did_you_mean = []
    if query and not books_qs.exists():
        titles = list(Book.objects.values_list("title", flat=True))
        did_you_mean = difflib.get_close_matches(query, titles, n=5, cutoff=0.6)

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

    paginator = Paginator(books_qs, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    top_categories = (
        Category.objects.filter(Q(parent__isnull=True) | Q(books__isnull=False))
        .distinct()
        .order_by("name")
    )
    popular_tags = Tag.objects.order_by("name")[:20]
    # Suggestions for the search box (lightweight, no extra endpoint):
    all_categories = Category.objects.order_by("name").only("name")
    sample_titles = Book.objects.order_by("-id").values_list("title", flat=True)[:50]
    return render(request, "myapp/pages/library_home.html", {
        "books": books,
        "top_categories": top_categories,
        "popular_tags": popular_tags,
        "selected_category": selected_category,
        "selected_tag": selected_tag,
        "search_query": query,
        "all_categories": all_categories,
        "sample_titles": sample_titles,
        "did_you_mean": did_you_mean,
    })


def aboutus(request):
    return render(request, "myapp/pages/aboutus.html")


def contact(request):
    context = {}
    if request.method == 'POST':
        data = request.POST
        topic = (data.get('topic') or '').strip()
        email = (data.get('email') or '').strip()
        detail = (data.get('detail') or '').strip()
        context.update({'topic': topic, 'email': email, 'detail': detail})
        if topic and email and detail:
            from ..models import ContactList
            ContactList.objects.create(topic=topic, email=email, detail=detail)
            context['message'] = 'The message has been received'
        else:
            context['message'] = 'Please fill in all fields: topic, email, and detail.'
    return render(request, 'myapp/pages/contact.html', context)


def home2(request):
    return HttpResponse("<h1>Hello world 2<h1>")


def addProduct(request):
    if request.method == "POST":
        product = Product(
            title=request.POST.get('title', '').strip(),
            description=request.POST.get('description', ''),
            price=request.POST.get('price') or None,
            quantity=request.POST.get('quantity') or None,
            picture=request.FILES.get('picture'),
            specfile=request.FILES.get('specfile')
        )
        product.save()
        return redirect('home-page')
    return render(request, "myapp/products/addProduct.html")


def handler404(request, exception):
    return render(request, "myapp/pages/404errorPage.html", status=404)
