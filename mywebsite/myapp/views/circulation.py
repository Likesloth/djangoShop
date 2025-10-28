from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import LoanCreateForm, LoanUpdateForm, LoanQuickCreateForm
from ..models import Loan, BookCopy
from ..services.policy import calculate_due_at, can_renew, compute_renew_due_at, can_borrow, FINE_RATE_PER_DAY
from ..models import Book, Fine


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


# Quick circulation desk (barcode-based) removed in favor of cart + pickup workflow and loans-by-user returns.
