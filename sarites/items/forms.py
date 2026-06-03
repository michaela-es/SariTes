from django import forms
from .models import Item

INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:outline-none'


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'price', 'qty']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Item name'}),
            'price': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01'}),
            'qty': forms.NumberInput(attrs={'class': INPUT}),
        }
