from django import forms
from .models import Transaction
from items.models import Item


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['item', 'transaction_type', 'qty', 'total', 'creditor', 'notes']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'creditor': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creditor'].required = False
        self.fields['total'].required = False
