from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from ..models import Book, Hold
from ..services.policy import HOLD_PICKUP_DAYS


@login_required(login_url='login')
def place_hold(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    # Prevent duplicate active holds by same user
    existing = Hold.objects.filter(book=book, user=request.user, canceled_at__isnull=True).exists()
    if existing:
        messages.info(request, "You already have a hold for this title.")
        return redirect('catalog-detail', book_id=book.id)

    # Compute next queue position
    last = Hold.objects.filter(book=book, canceled_at__isnull=True).order_by('-queue_position').first()
    next_pos = (last.queue_position + 1) if last else 1
    Hold.objects.create(book=book, user=request.user, queue_position=next_pos)
    messages.success(request, "Hold placed. We'll notify when it's ready for pickup.")
    return redirect('catalog-detail', book_id=book.id)


@login_required(login_url='login')
def cancel_hold(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    hold = Hold.objects.filter(book=book, user=request.user, canceled_at__isnull=True).first()
    if not hold:
        messages.info(request, "No active hold to cancel.")
        return redirect('catalog-detail', book_id=book.id)
    hold.canceled_at = timezone.now()
    hold.save(update_fields=["canceled_at"])
    messages.success(request, "Hold canceled.")
    return redirect('catalog-detail', book_id=book.id)


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def holds_manage_ready(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    # Mark the first in queue as ready
    next_hold = Hold.objects.filter(book=book, canceled_at__isnull=True, is_ready=False).order_by('queue_position', 'created_at').first()
    if next_hold:
        next_hold.is_ready = True
        next_hold.expires_at = timezone.now() + timezone.timedelta(days=HOLD_PICKUP_DAYS)
        next_hold.save(update_fields=["is_ready", "expires_at"])
        messages.success(request, f"Hold marked ready for {next_hold.user.username}.")
    else:
        messages.info(request, "No queued holds to mark ready.")
    return redirect('catalog-detail', book_id=book.id)


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def holds_expire_ready(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    ready = Hold.objects.filter(book=book, is_ready=True, canceled_at__isnull=True, expires_at__lt=timezone.now()).first()
    if ready:
        ready.canceled_at = timezone.now()
        ready.save(update_fields=["canceled_at"])
        messages.success(request, "Expired ready hold.")
    else:
        messages.info(request, "No expired ready holds.")
    return redirect('catalog-detail', book_id=book.id)
