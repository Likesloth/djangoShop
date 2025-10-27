from django import forms

from .models import Action, Loan


class ActionCreateForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['contact', 'name', 'detail']
        widgets = {
            'contact': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Action name'}),
            'detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the action'}),
        }


class ActionUpdateForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['contact', 'name', 'detail', 'complete']
        widgets = {
            'contact': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'complete': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ActionQuickCreateForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['name', 'detail']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Action name'}),
            'detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the action'}),
        }


# ==== Library: Loan forms ====

class LoanCreateForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["borrower", "copy", "due_at", "note"]
        widgets = {
            "borrower": forms.Select(attrs={"class": "form-select"}),
            "copy": forms.Select(attrs={"class": "form-select"}),
            "due_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional notes"}),
        }

    def clean(self):
        cleaned = super().clean()
        copy = cleaned.get("copy")
        if copy is None:
            return cleaned
        # Prevent checkout if copy is not AVAILABLE
        from .models import BookCopy, Loan
        if copy.status != BookCopy.STATUS_AVAILABLE:
            self.add_error("copy", "This copy is not available for checkout.")
        # Prevent duplicate active loan for the same copy
        if Loan.objects.filter(copy=copy, returned_at__isnull=True).exists():
            self.add_error("copy", "This copy already has an active loan.")
        return cleaned


class LoanUpdateForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["due_at", "returned_at", "renew_count", "note"]
        widgets = {
            "due_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "returned_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "renew_count": forms.NumberInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class LoanQuickCreateForm(forms.ModelForm):
    """
    For circulation desk: set borrower/copy in the view (commit=False),
    only let staff tweak due_at and add a note.
    """

    class Meta:
        model = Loan
        fields = ["due_at", "note"]
        widgets = {
            "due_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
