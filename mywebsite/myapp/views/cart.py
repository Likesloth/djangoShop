from datetime import timedelta, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.utils import timezone

from ..models import Book, Cart, CartItem, PickupRequest, PickupRequestItem, BookCopy
from ..services.policy import HOLD_PICKUP_DAYS


def _get_or_create_cart(user) -> Cart:
    cart = Cart.objects.filter(owner=user).order_by('-updated_at').first()
    if cart is None:
        cart = Cart.objects.create(owner=user)
    return cart


@login_required(login_url='login')
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    # Prefetch copies for availability dropdowns
    items = cart.items.select_related('book').prefetch_related('book__copies').all()
    return render(request, 'myapp/cart/cart.html', {
        'cart': cart,
        'items': items,
    })


@login_required(login_url='login')
def cart_add(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    cart = _get_or_create_cart(request.user)
    CartItem.objects.get_or_create(cart=cart, book=book)
    messages.success(request, f'Added "{book.title}" to your cart.')
    return redirect('catalog-detail', book_id=book.id)


@login_required(login_url='login')
def cart_remove(request, book_id):
    cart = _get_or_create_cart(request.user)
    try:
        item = CartItem.objects.get(cart=cart, book_id=book_id)
        item.delete()
        messages.success(request, 'Removed from cart.')
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in your cart.')
    return redirect('cart-view')


@login_required(login_url='login')
@transaction.atomic
def cart_place_request(request):
    cart = _get_or_create_cart(request.user)
    items = list(cart.items.select_related('book').all())
    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart-view')

    # pickup_by: either provided (YYYY-MM-DD) or default today + HOLD_PICKUP_DAYS
    pickup_by_raw = (request.POST.get('pickup_by') or '').strip()
    try:
        pickup_by = date.fromisoformat(pickup_by_raw) if pickup_by_raw else None
    except Exception:
        pickup_by = None
    if pickup_by is None:
        pickup_by = (timezone.now() + timedelta(days=HOLD_PICKUP_DAYS)).date()

    pickup_location = (request.POST.get('pickup_location') or '').strip()

    pr = PickupRequest.objects.create(
        requester=request.user,
        pickup_location=pickup_location,
        pickup_by=pickup_by,
        status=PickupRequest.STATUS_PENDING,
    )
    for it in items:
        # Optional: user-selected copy per item
        selected_copy_id = (request.POST.get(f'copy_{it.id}') or '').strip()
        pri = PickupRequestItem.objects.create(request=pr, book=it.book)
        if selected_copy_id:
            try:
                copy = BookCopy.objects.select_for_update().get(id=selected_copy_id, book=it.book)
            except BookCopy.DoesNotExist:
                copy = None
            if copy and copy.status == BookCopy.STATUS_AVAILABLE:
                pri.assigned_copy = copy
                pri.save(update_fields=['assigned_copy'])
                copy.status = BookCopy.STATUS_RESERVED
                copy.save(update_fields=['status'])
    # Clear cart
    cart.items.all().delete()

    messages.success(request, 'Request placed. You will be notified when ready for pickup.')
    return redirect('my-requests')
