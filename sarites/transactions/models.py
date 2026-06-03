from django.db import models
from items.models import Item
from creditors.models import Creditor


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('stock_in', 'Stock In'),
        ('stock_out', 'Stock Out'),
        ('sale', 'Sale'),
        ('credit_sale', 'Credit Sale'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    qty = models.IntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    creditor = models.ForeignKey(Creditor, on_delete=models.SET_NULL, blank=True, null=True, related_name='transactions')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.total is None:
            self.total = self.item.price * self.qty
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item.name} x{self.qty}"
