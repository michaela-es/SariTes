from django.db import models


class Creditor(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_balance(self):
        from transactions.models import Transaction
        from django.db.models import Sum
        result = Transaction.objects.filter(
            creditor=self, transaction_type='credit_sale'
        ).aggregate(total=Sum('total'))
        return result['total'] or 0

    @property
    def transaction_count(self):
        return self.transactions.count()
