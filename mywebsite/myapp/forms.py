from django import forms

from .models import Action


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
