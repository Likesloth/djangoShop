from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import Loan, Fine
from ..services.policy import can_renew, compute_renew_due_at


@login_required(login_url='login')
def my_loans(request):
    loans_qs = Loan.objects.filter(borrower=request.user).select_related("copy", "copy__book").order_by("-checked_out_at")
    active = [l for l in loans_qs if l.returned_at is None]
    past = [l for l in loans_qs if l.returned_at is not None]

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()
        loan_id = request.POST.get('loan_id')
        if action == 'renew' and loan_id:
            loan = get_object_or_404(Loan, pk=loan_id, borrower=request.user)
            if can_renew(loan):
                new_due = compute_renew_due_at(timezone.now(), loan)
                loan.due_at = new_due
                loan.renew_count += 1
                loan.save(update_fields=["due_at", "renew_count"])
                messages.success(request, f"Renewed. New due: {new_due:%Y-%m-%d %H:%M}.")
            else:
                messages.error(request, "Cannot renew this loan.")
            return redirect('my-loans')

    return render(request, 'myapp/account/my_loans.html', {
        'active_loans': active,
        'past_loans': past,
    })


@login_required(login_url='login')
def my_fines(request):
    fines = Fine.objects.filter(loan__borrower=request.user).select_related('loan', 'loan__copy', 'loan__copy__book')
    return render(request, 'myapp/account/my_fines.html', {
        'unpaid': [f for f in fines if not f.paid_at],
        'paid': [f for f in fines if f.paid_at],
    })
