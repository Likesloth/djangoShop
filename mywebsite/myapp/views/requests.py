from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import (
    PickupRequest,
    PickupRequestItem,
    BookCopy,
    Loan,
)
from ..services.policy import calculate_due_at, active_loan_limit


@login_required(login_url='login')
def my_requests(request):
    reqs = (
        PickupRequest.objects.filter(requester=request.user)
        .order_by('-requested_at')
        .prefetch_related('items', 'items__book', 'items__assigned_copy', 'items__assigned_copy__book')
    )
    return render(request, 'myapp/account/my_requests.html', {'requests': reqs})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def requests_queue(request):
    qs = (
        PickupRequest.objects.filter(status__in=[
            PickupRequest.STATUS_PENDING,
            PickupRequest.STATUS_PREPARING,
            PickupRequest.STATUS_READY,
        ])
        .order_by('status', 'requested_at')
    )
    return render(request, 'myapp/staff/requests_list.html', {'requests': qs})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def request_detail(request, request_id):
    pr = get_object_or_404(
        PickupRequest.objects.prefetch_related('items', 'items__book', 'items__assigned_copy', 'requester'),
        pk=request_id,
    )
    return render(request, 'myapp/staff/request_detail.html', {'pr': pr})


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def set_pickup_by(request, request_id):
    pr = get_object_or_404(PickupRequest, pk=request_id)
    if request.method != 'POST':
        return redirect('staff-request-detail', request_id=pr.id)
    raw = (request.POST.get('pickup_by') or '').strip()
    if not raw:
        pr.pickup_by = None
        pr.save(update_fields=['pickup_by'])
        messages.success(request, 'Cleared pickup date.')
        return redirect('staff-request-detail', request_id=pr.id)
    try:
        # Expect ISO date (YYYY-MM-DD)
        from datetime import date

        value = date.fromisoformat(raw)
    except Exception:
        messages.error(request, 'Invalid date format. Use YYYY-MM-DD.')
        return redirect('staff-request-detail', request_id=pr.id)
    pr.pickup_by = value
    pr.save(update_fields=['pickup_by'])
    messages.success(request, 'Pickup date updated.')
    return redirect('staff-request-detail', request_id=pr.id)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
@transaction.atomic
def assign_item_copy(request, request_id, item_id):
    pr = get_object_or_404(PickupRequest, pk=request_id)
    item = get_object_or_404(PickupRequestItem, pk=item_id, request=pr)
    barcode = (request.POST.get('barcode') or '').strip()
    if not barcode:
        messages.error(request, 'Please enter a barcode to assign.')
        return redirect('staff-request-detail', request_id=pr.id)

    copy = BookCopy.objects.filter(barcode=barcode).select_for_update().first()
    if copy is None:
        messages.error(request, 'Copy not found.')
        return redirect('staff-request-detail', request_id=pr.id)
    if copy.book_id != item.book_id:
        messages.error(request, 'This barcode does not match the requested title.')
        return redirect('staff-request-detail', request_id=pr.id)
    if copy.status != BookCopy.STATUS_AVAILABLE:
        messages.error(request, 'This copy is not available to reserve.')
        return redirect('staff-request-detail', request_id=pr.id)

    # Assign and reserve
    item.assigned_copy = copy
    item.save(update_fields=['assigned_copy'])
    copy.status = BookCopy.STATUS_RESERVED
    copy.save(update_fields=['status'])
    if pr.status == PickupRequest.STATUS_PENDING:
        pr.status = PickupRequest.STATUS_PREPARING
        pr.prepared_at = timezone.now()
        pr.save(update_fields=['status', 'prepared_at'])
    messages.success(request, f'Assigned copy {copy.barcode}.')
    return redirect('staff-request-detail', request_id=pr.id)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def mark_request_ready(request, request_id):
    pr = get_object_or_404(PickupRequest, pk=request_id)
    missing = pr.items.filter(assigned_copy__isnull=True).exists()
    if missing:
        messages.error(request, 'All items must be assigned before marking ready.')
        return redirect('staff-request-detail', request_id=pr.id)
    if not pr.pickup_by:
        messages.error(request, 'Set a pickup date before marking ready.')
        return redirect('staff-request-detail', request_id=pr.id)
    pr.status = PickupRequest.STATUS_READY
    pr.ready_at = timezone.now()
    pr.save(update_fields=['status', 'ready_at'])
    messages.success(request, 'Marked as ready for pickup.')
    return redirect('staff-requests-queue')


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
@transaction.atomic
def confirm_pickup(request, request_id):
    pr = get_object_or_404(PickupRequest.objects.select_for_update(), pk=request_id)
    if pr.status not in (PickupRequest.STATUS_READY, PickupRequest.STATUS_PREPARING):
        messages.error(request, 'Request is not ready for pickup.')
        return redirect('staff-request-detail', request_id=pr.id)
    items = list(pr.items.select_related('assigned_copy', 'book'))
    if any(it.assigned_copy_id is None for it in items):
        messages.error(request, 'All items need assigned copies before pickup.')
        return redirect('staff-request-detail', request_id=pr.id)

    # Enforce loan limit for borrower
    current_active = Loan.objects.filter(borrower=pr.requester, returned_at__isnull=True).count()
    limit = active_loan_limit(pr.requester)
    if current_active + len(items) > limit:
        messages.error(request, f'Borrower exceeds loan limit (limit {limit}, has {current_active}, requested {len(items)}).')
        return redirect('staff-request-detail', request_id=pr.id)

    now = timezone.now()
    due_at = calculate_due_at(now, pr.requester)
    for it in items:
        copy = it.assigned_copy
        if copy.status not in (BookCopy.STATUS_RESERVED, BookCopy.STATUS_AVAILABLE):
            messages.error(request, f'Copy {copy.barcode} not reservable for checkout.')
            return redirect('staff-request-detail', request_id=pr.id)
    # Create loans and flip statuses
    for it in items:
        copy = it.assigned_copy
        Loan.objects.create(borrower=pr.requester, copy=copy, due_at=due_at)
        copy.status = BookCopy.STATUS_ON_LOAN
        copy.save(update_fields=['status'])

    pr.status = PickupRequest.STATUS_PICKED_UP
    pr.picked_up_at = now
    pr.save(update_fields=['status', 'picked_up_at'])
    messages.success(request, 'Pickup confirmed and loans created.')
    return redirect('staff-requests-queue')


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
@transaction.atomic
def unassign_item_copy(request, request_id, item_id):
    pr = get_object_or_404(PickupRequest, pk=request_id)
    item = get_object_or_404(PickupRequestItem, pk=item_id, request=pr)
    if item.assigned_copy_id:
        copy = item.assigned_copy
        if copy.status == BookCopy.STATUS_RESERVED:
            copy.status = BookCopy.STATUS_AVAILABLE
            copy.save(update_fields=['status'])
        item.assigned_copy = None
        item.save(update_fields=['assigned_copy'])
        messages.success(request, 'Unassigned copy and released reservation.')
    else:
        messages.info(request, 'Item had no assigned copy.')
    return redirect('staff-request-detail', request_id=pr.id)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
@transaction.atomic
def cancel_request(request, request_id):
    pr = get_object_or_404(PickupRequest.objects.select_for_update(), pk=request_id)
    # Release any reserved copies
    for it in pr.items.select_related('assigned_copy'):
        if it.assigned_copy_id and it.assigned_copy.status == BookCopy.STATUS_RESERVED:
            it.assigned_copy.status = BookCopy.STATUS_AVAILABLE
            it.assigned_copy.save(update_fields=['status'])
    pr.status = PickupRequest.STATUS_CANCELED
    pr.canceled_at = timezone.now()
    pr.save(update_fields=['status', 'canceled_at'])
    messages.success(request, 'Request canceled and reservations released.')
    return redirect('staff-requests-queue')
