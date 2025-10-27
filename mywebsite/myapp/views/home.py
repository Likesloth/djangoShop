from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.db.models import Q, Count

from ..models import Product, Book, BookCopy


def home(request):
    all_products = Product.objects.all().order_by('-id')
    paginator = Paginator(all_products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "myapp/pages/home.html", {"allproduct": page_obj})


def library_home(request):
    books_qs = (
        Book.objects.all()
        .annotate(available_count=Count("copies", filter=Q(copies__status=BookCopy.STATUS_AVAILABLE)))
        .order_by("-id")
    )
    paginator = Paginator(books_qs, 6)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    return render(request, "myapp/pages/library_home.html", {"books": books})


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

