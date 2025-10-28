import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from ..models import Book, BookCopy, Loan, Fine, Author
from ..services.policy import FINE_RATE_PER_DAY


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def copy_status_update(request, copy_id, status):
    copy = get_object_or_404(BookCopy, pk=copy_id)
    if status not in dict(BookCopy.STATUS_CHOICES):
        messages.error(request, 'Invalid status.')
        return redirect('catalog-detail', book_id=copy.book_id)
    copy.status = status
    copy.save(update_fields=['status'])
    messages.success(request, f'Copy {copy.barcode} set to {status}.')
    return redirect('catalog-detail', book_id=copy.book_id)


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def overdues_list(request):
    now = timezone.now()
    loans = Loan.objects.filter(returned_at__isnull=True, due_at__lt=now).select_related('borrower', 'copy', 'copy__book')
    return render(request, 'myapp/staff/overdues.html', {'loans': loans, 'now': now})


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def fines_ledger(request):
    fines = Fine.objects.select_related('loan', 'loan__borrower', 'loan__copy', 'loan__copy__book')
    unpaid = fines.filter(paid_at__isnull=True)
    paid = fines.filter(paid_at__isnull=False)
    return render(request, 'myapp/staff/fines_ledger.html', {'unpaid': unpaid, 'paid': paid})


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def fine_mark_paid(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id)
    fine.paid_at = timezone.now()
    fine.save(update_fields=['paid_at'])
    messages.success(request, 'Fine marked as paid.')
    return redirect('staff-fines')



# Reports (CSV)
@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def report_overdues_csv(request):
    now = timezone.now()
    loans = Loan.objects.filter(returned_at__isnull=True, due_at__lt=now).select_related('borrower', 'copy', 'copy__book')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="overdues.csv"'
    writer = csv.writer(response)
    writer.writerow(['Book', 'Barcode', 'Borrower', 'Due At'])
    for loan in loans:
        writer.writerow([loan.copy.book.title, loan.copy.barcode, loan.borrower.username, loan.due_at.isoformat()])
    return response


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def report_top_borrowed_csv(request):
    agg = (
        Loan.objects.values('copy__book__title')
        .annotate(count=Count('id'))
        .order_by('-count')[:100]
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="top_borrowed.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Loans'])
    for row in agg:
        writer.writerow([row['copy__book__title'], row['count']])
    return response


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def report_fines_summary_csv(request):
    total = Fine.objects.aggregate(total=Sum('amount'))['total'] or 0
    unpaid = Fine.objects.filter(paid_at__isnull=True).aggregate(total=Sum('amount'))['total'] or 0
    paid = Fine.objects.filter(paid_at__isnull=False).aggregate(total=Sum('amount'))['total'] or 0
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fines_summary.csv"'
    writer = csv.writer(response)
    writer.writerow(['Metric', 'Amount'])
    writer.writerow(['Total fines', total])
    writer.writerow(['Unpaid fines', unpaid])
    writer.writerow(['Paid fines', paid])
    return response


# CSV import for books
# CSV import removed by request; use manual add or Admin instead.


def _ensure_category_from_path(path_str):
    if not path_str:
        return None
    parts = [p.strip() for p in path_str.split('>') if p.strip()]
    if not parts:
        return None
    from ..models import Category
    parent = None
    for name in parts:
        obj, _ = Category.objects.get_or_create(name=name, slug=slugify(name), parent=parent)
        parent = obj
    return parent


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def book_create_manual(request):
    if request.method == 'POST':
        isbn13 = (request.POST.get('isbn13') or '').strip()
        title = (request.POST.get('title') or '').strip()
        language = (request.POST.get('language') or 'EN').strip()
        publish_year_raw = (request.POST.get('publish_year') or '').strip()
        authors_str = (request.POST.get('authors') or '').strip()
        category_path = (request.POST.get('category_path') or '').strip()
        tags_str = (request.POST.get('tags') or '').strip()
        first_barcode = (request.POST.get('first_barcode') or '').strip()
        location = (request.POST.get('location') or 'Main').strip()
        cover_file = request.FILES.get('cover')

        if not isbn13 or not title:
            messages.error(request, 'ISBN13 and Title are required.')
            return render(request, 'myapp/staff/book_create.html')

        try:
            publish_year = int(publish_year_raw) if publish_year_raw else None
        except Exception:
            publish_year = None

        book, created = Book.objects.get_or_create(
            isbn13=isbn13,
            defaults={
                'title': title,
                'language': language,
                'publish_year': publish_year,
            }
        )
        if not created:
            book.title = title or book.title
            book.language = language or book.language
            if publish_year is not None:
                book.publish_year = publish_year
        if cover_file:
            book.cover = cover_file

        # Category
        category = _ensure_category_from_path(category_path)
        if category:
            book.category = category

        book.save()

        # Authors
        for full_name in [a.strip() for a in authors_str.split(';') if a.strip()]:
            author, _ = Author.objects.get_or_create(full_name=full_name)
            book.authors.add(author)

        # Tags
        from ..models import Tag
        for name in [t.strip() for t in tags_str.split(';') if t.strip()]:
            tag, _ = Tag.objects.get_or_create(name=name, slug=slugify(name))
            book.tags.add(tag)

        # First copy
        if first_barcode:
            BookCopy.objects.get_or_create(
                barcode=first_barcode,
                defaults={'book': book, 'location': location, 'status': BookCopy.STATUS_AVAILABLE}
            )

        messages.success(request, 'Book saved.')
        return redirect('catalog-detail', book_id=book.id)

    return render(request, 'myapp/staff/book_create.html')


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def reports_dashboard(request):
    now = timezone.now()
    overdue_loans = Loan.objects.filter(returned_at__isnull=True, due_at__lt=now)
    overdue_count = overdue_loans.count()

    top_borrowed_qs = (
        Loan.objects.values('copy__book__title')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    fines_total = Fine.objects.aggregate(total=Sum('amount'))['total'] or 0
    fines_unpaid = Fine.objects.filter(paid_at__isnull=True).aggregate(total=Sum('amount'))['total'] or 0
    fines_paid = Fine.objects.filter(paid_at__isnull=False).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'now': now,
        'overdue_count': overdue_count,
        'top_borrowed': top_borrowed_qs,
        'fines_total': fines_total,
        'fines_unpaid': fines_unpaid,
        'fines_paid': fines_paid,
    }
    return render(request, 'myapp/staff/reports.html', context)


# Active loans by user with return action
@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff or user.is_superuser, login_url='login')
def loans_by_user(request):
    from django.contrib.auth.models import User
    borrower = None
    q = (request.GET.get('q') or '').strip()
    if q:
        borrower = (
            User.objects.filter(Q(username__iexact=q) | Q(email__iexact=q)).first()
        )

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()
        loan_id = (request.POST.get('loan_id') or '').strip()
        if action == 'return' and loan_id:
            loan = get_object_or_404(Loan.objects.select_related('copy', 'borrower'), pk=loan_id)
            if loan.returned_at is None:
                loan.returned_at = timezone.now()
                loan.save(update_fields=['returned_at'])
                if loan.copy and loan.copy.status != BookCopy.STATUS_AVAILABLE:
                    loan.copy.status = BookCopy.STATUS_AVAILABLE
                    loan.copy.save(update_fields=['status'])
                # Overdue fine (same logic as circulation desk)
                if loan.due_at and loan.returned_at > loan.due_at:
                    days_over = (loan.returned_at.date() - loan.due_at.date()).days
                    if days_over > 0:
                        Fine.objects.create(loan=loan, amount=days_over * FINE_RATE_PER_DAY, reason=f"Overdue {days_over} day(s)")
                messages.success(request, f"Marked returned: {loan.copy.barcode} for {loan.borrower.username}.")
            return redirect(request.path + (f"?q={q}" if q else ""))

    loans_qs = Loan.objects.filter(returned_at__isnull=True).select_related('borrower', 'copy', 'copy__book').order_by('borrower__username', 'due_at')
    if borrower:
        loans_qs = loans_qs.filter(borrower=borrower)

    return render(request, 'myapp/staff/loans_by_user.html', {
        'q': q,
        'borrower': borrower,
        'loans': loans_qs,
        'now': timezone.now(),
    })
