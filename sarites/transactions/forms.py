from django import forms
from .models import Transaction

INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:outline-none'
SELECT = 'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:outline-none'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['item', 'transaction_type', 'qty', 'total', 'creditor', 'notes']
        widgets = {
            'item': forms.Select(attrs={'class': SELECT}),
            'transaction_type': forms.Select(attrs={'class': SELECT}),
            'qty': forms.NumberInput(attrs={'class': INPUT}),
            'total': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01'}),
            'creditor': forms.Select(attrs={'class': SELECT}),
            'notes': forms.Textarea(attrs={'class': INPUT, 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creditor'].required = False
        self.fields['total'].required = False
