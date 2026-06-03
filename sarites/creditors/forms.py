from django import forms
from .models import Creditor

INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:outline-none'


class CreditorForm(forms.ModelForm):
    class Meta:
        model = Creditor
        fields = ['name', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Creditor name'}),
            'contact_info': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Contact info'}),
        }
