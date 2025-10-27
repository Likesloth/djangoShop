from datetime import timedelta
from decimal import Decimal

try:
    # Import lazily to avoid issues during migrations
    from ..models import Policy
except Exception:
    Policy = None


# Simple, configurable policy values
LOAN_PERIODS = {
    "student": 14,
    "member": 14,
    "lecturer": 28,
    "default": 14,
}

MAX_RENEWALS = 2
FINE_RATE_PER_DAY = 5  # THB/day
HOLD_PICKUP_DAYS = 3
LIMITS = {
    "student": 5,
    "member": 5,
    "lecturer": 10,
    "default": 5,
}


def loan_period_days(user) -> int:
    # If Policy table exists, prefer dynamic settings
    if Policy is not None:
        try:
            cfg = Policy.current()
            if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
                return int(cfg.lecturer_loan_days)
            role = (getattr(getattr(user, "profile", None), "usertype", "student") or "student").lower()
            return int(cfg.student_loan_days) if role in ("student", "member") else int(cfg.lecturer_loan_days)
        except Exception:
            pass
    # Fallback constants
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return LOAN_PERIODS.get("lecturer", 28)
    role = (getattr(getattr(user, "profile", None), "usertype", "default") or "default").lower()
    return LOAN_PERIODS.get(role, LOAN_PERIODS["default"])


def calculate_due_at(now, user):
    return now + timedelta(days=loan_period_days(user))


def can_renew(loan) -> bool:
    # MVP: limit by count only. Add hold checks later.
    return (loan.returned_at is None) and (loan.renew_count < MAX_RENEWALS)


def compute_renew_due_at(now, loan):
    # Extend from the later of due_at or now by the user's policy period
    from_date = loan.due_at if loan.due_at and loan.due_at > now else now
    return from_date + timedelta(days=loan_period_days(loan.borrower))


def active_loan_limit(user) -> int:
    if Policy is not None:
        try:
            cfg = Policy.current()
            if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
                return int(cfg.lecturer_loan_limit)
            role = (getattr(getattr(user, "profile", None), "usertype", "student") or "student").lower()
            return int(cfg.student_loan_limit) if role in ("student", "member") else int(cfg.lecturer_loan_limit)
        except Exception:
            pass
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return LIMITS.get("lecturer", 10)
    role = (getattr(getattr(user, "profile", None), "usertype", "default") or "default").lower()
    return LIMITS.get(role, LIMITS["default"])


def can_borrow(user, current_active_count: int) -> bool:
    return current_active_count < active_loan_limit(user)
