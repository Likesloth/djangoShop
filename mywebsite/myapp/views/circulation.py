from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from ..forms import LoanCreateForm, LoanUpdateForm, LoanQuickCreateForm
from ..models import Loan, BookCopy
from ..services.policy import calculate_due_at, can_renew, compute_renew_due_at, can_borrow, FINE_RATE_PER_DAY, HOLD_PICKUP_DAYS
from ..models import Book, Hold, Fine


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def loan_create(request):
    if request.method == "POST":
        form = LoanCreateForm(request.POST)
        if form.is_valid():
            loan = form.save()
            loan.copy.status = BookCopy.STATUS_ON_LOAN
            loan.copy.save(update_fields=["status"])
            messages.success(request, "Loan created.")
            return redirect('catalog-list')
    else:
        form = LoanCreateForm()
    return render(request, "myapp/circulation/loan_form.html", {"form": form})


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def loan_update(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    if request.method == "POST":
        form = LoanUpdateForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save()
            if loan.returned_at:
                loan.copy.status = BookCopy.STATUS_AVAILABLE
                loan.copy.save(update_fields=["status"]) 
            messages.success(request, "Loan updated.")
            return redirect('catalog-list')
    else:
        form = LoanUpdateForm(instance=loan)
    return render(request, "myapp/circulation/loan_form.html", {"form": form, "loan": loan})


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def quick_checkout(request):
    barcode = (request.GET.get("barcode") or request.POST.get("barcode") or "").strip()
    copy = None
    active_loan = None
    if barcode:
        copy = get_object_or_404(BookCopy, barcode=barcode)
        active_loan = Loan.objects.filter(copy=copy, returned_at__isnull=True).select_related("borrower").first()

    default_due = timezone.now() + timedelta(days=14)

    if request.method == "POST":
        # Return flow
        if (request.POST.get("action") or "").strip() == "return" and copy is not None and active_loan is not None:
            active_loan.returned_at = timezone.now()
            active_loan.save(update_fields=["returned_at"])
            copy.status = BookCopy.STATUS_AVAILABLE
            copy.save(update_fields=["status"])
            # Fine calculation on return if overdue
            if active_loan.due_at and active_loan.returned_at > active_loan.due_at:
                days_over = (active_loan.returned_at.date() - active_loan.due_at.date()).days
                if days_over > 0:
                    amount = days_over * FINE_RATE_PER_DAY
                    Fine.objects.create(loan=active_loan, amount=amount, reason=f"Overdue {days_over} day(s)")
            # Holds: mark next hold ready
            next_hold = (
                Hold.objects.filter(book=copy.book, canceled_at__isnull=True, is_ready=False)
                .order_by("queue_position", "created_at")
                .first()
            )
            if next_hold:
                next_hold.is_ready = True
                next_hold.expires_at = timezone.now() + timezone.timedelta(days=HOLD_PICKUP_DAYS)
                next_hold.save(update_fields=["is_ready", "expires_at"])
            messages.success(request, f"Returned {copy.barcode} from {active_loan.borrower.username}.")
            return redirect(f"{reverse('circulation-desk')}?barcode={barcode}")

        # Renew flow
        if (request.POST.get("action") or "").strip() == "renew" and copy is not None and active_loan is not None:
            if can_renew(active_loan):
                new_due = compute_renew_due_at(timezone.now(), active_loan)
                active_loan.due_at = new_due
                active_loan.renew_count += 1
                active_loan.save(update_fields=["due_at", "renew_count"])
                messages.success(request, f"Renewed. New due: {new_due:%Y-%m-%d %H:%M}.")
            else:
                messages.error(request, "Renewal not allowed (limit reached or returned).")
            return redirect(f"{reverse('circulation-desk')}?barcode={barcode}")

        # Checkout flow
        post_data = request.POST.copy()
        borrower_identifier = (post_data.get("borrower_username") or "").strip()
        borrower = None
        if borrower_identifier:
            borrower = (
                User.objects.filter(Q(username__iexact=borrower_identifier) | Q(email__iexact=borrower_identifier))
                .first()
            )
        if not (post_data.get("due_at") or "").strip():
            computed_due = calculate_due_at(timezone.now(), borrower) if borrower else default_due
            post_data["due_at"] = computed_due.strftime("%Y-%m-%dT%H:%M")
        form = LoanQuickCreateForm(post_data)

        if not borrower:
            messages.error(request, "Borrower not found. Use username or email (case-insensitive).")
        elif copy is None:
            messages.error(request, "Please scan or enter a valid barcode.")
        else:
            active_loan_exists = active_loan is not None
            if copy.status != BookCopy.STATUS_AVAILABLE or active_loan_exists:
                messages.error(request, "This copy is not available for checkout.")
            # Enforce loan limit
            active_count = Loan.objects.filter(borrower=borrower, returned_at__isnull=True).count()
            if not can_borrow(borrower, active_count):
                messages.error(request, "Borrower reached loan limit.")
            # Holds policy: if there is a ready hold for this book and it's not for this borrower, block
            ready_hold = Hold.objects.filter(book=copy.book, is_ready=True, canceled_at__isnull=True, expires_at__gt=timezone.now()).order_by("queue_position", "created_at").first()
            if ready_hold and ready_hold.user_id != borrower.id:
                messages.error(request, "This title is reserved for another borrower.")
            # If there is a queue and borrower is not first, block
            queue_first = Hold.objects.filter(book=copy.book, canceled_at__isnull=True, is_ready=False).order_by("queue_position", "created_at").first()
            if queue_first and queue_first.user_id != borrower.id:
                messages.error(request, "There is a hold queue for this title.")

        violations = []
        if borrower:
            active_count = Loan.objects.filter(borrower=borrower, returned_at__isnull=True).count()
            if not can_borrow(borrower, active_count):
                violations.append("limit")
        ready_hold = Hold.objects.filter(book=copy.book, is_ready=True, canceled_at__isnull=True, expires_at__gt=timezone.now()).order_by("queue_position", "created_at").first() if copy else None
        queue_first = Hold.objects.filter(book=copy.book, canceled_at__isnull=True, is_ready=False).order_by("queue_position", "created_at").first() if copy else None

        if form.is_valid() and borrower and copy is not None and copy.status == BookCopy.STATUS_AVAILABLE and not Loan.objects.filter(copy=copy, returned_at__isnull=True).exists() and not violations and not (ready_hold and ready_hold.user_id != borrower.id) and not (queue_first and queue_first.user_id != borrower.id):
            loan = form.save(commit=False)
            loan.borrower = borrower
            loan.copy = copy
            loan.save()
            copy.status = BookCopy.STATUS_ON_LOAN
            copy.save(update_fields=["status"])
            # If borrower had a ready hold, clear it
            if ready_hold and ready_hold.user_id == borrower.id:
                ready_hold.canceled_at = timezone.now()
                ready_hold.save(update_fields=["canceled_at"])
            messages.success(request, f"Checked out {copy.barcode} to {borrower.username}.")
            return redirect('circulation-desk')
    else:
        form = LoanQuickCreateForm(initial={"due_at": default_due})

    return render(request, "myapp/circulation/quick_checkout.html", {"form": form, "copy": copy, "barcode": barcode, "active_loan": active_loan})
