from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from myapp.models import Loan


class Command(BaseCommand):
    help = "Simulate sending due soon and overdue email reminders (logs to console)."

    def handle(self, *args, **options):
        now = timezone.now()
        due_soon_from = now + timedelta(days=1)
        due_soon_to = now + timedelta(days=2)

        due_soon = Loan.objects.filter(returned_at__isnull=True, due_at__gte=due_soon_from, due_at__lte=due_soon_to)
        overdue = Loan.objects.filter(returned_at__isnull=True, due_at__lt=now)

        self.stdout.write(self.style.NOTICE(f"Due soon (T-2..T-1 days): {due_soon.count()}"))
        for loan in due_soon.select_related('borrower', 'copy', 'copy__book'):
            self.stdout.write(f"[Due Soon] user={loan.borrower.username} title={loan.copy.book.title} due={loan.due_at:%Y-%m-%d %H:%M}")

        self.stdout.write(self.style.NOTICE(f"Overdue: {overdue.count()}"))
        for loan in overdue.select_related('borrower', 'copy', 'copy__book'):
            self.stdout.write(f"[Overdue] user={loan.borrower.username} title={loan.copy.book.title} due={loan.due_at:%Y-%m-%d %H:%M}")

        self.stdout.write(self.style.SUCCESS("Reminder run complete (simulated)."))

