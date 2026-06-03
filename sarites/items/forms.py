from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'price', 'qty']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control'}),
        }
