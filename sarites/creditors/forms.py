from django import forms
from .models import Creditor


class CreditorForm(forms.ModelForm):
    class Meta:
        model = Creditor
        fields = ['name', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Creditor name'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact info'}),
        }
