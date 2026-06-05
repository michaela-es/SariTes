from django.db import migrations
from decimal import Decimal


def backfill_unit_price(apps, schema_editor):
    Transaction = apps.get_model('transactions', 'Transaction')
    for t in Transaction.objects.filter(unit_price__isnull=True).iterator():
        if t.qty and t.total:
            t.unit_price = t.total / Decimal(str(t.qty))
            t.save(update_fields=['unit_price'])


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transaction_unit_price'),
    ]

    operations = [
        migrations.RunPython(backfill_unit_price, migrations.RunPython.noop),
    ]
