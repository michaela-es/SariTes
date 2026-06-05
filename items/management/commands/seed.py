from django.core.management.base import BaseCommand
from items.models import Item
from creditors.models import Creditor
from transactions.models import Transaction


class Command(BaseCommand):
    help = 'Seeds the database with sample items, creditors, and transactions'

    def handle(self, *args, **options):
        items_data = [
            ('Coca-Cola', 25.00, 100),
            ('Rice 1kg', 55.00, 50),
            ('Cooking Oil 1L', 40.00, 30),
            ('Sardines', 20.00, 80),
            ('Noodles Cup', 18.00, 60),
            ('Sugar 1kg', 60.00, 25),
            ('Coffee 3in1', 8.00, 120),
            ('Milk 1L', 95.00, 20),
            ('Bread Loaf', 45.00, 15),
            ('Eggs (per tray)', 210.00, 10),
            ('Shampoo Sachet', 7.00, 200),
            ('Soap Bar', 15.00, 90),
            ('Toothpaste', 35.00, 40),
            ('Canned Tuna', 22.00, 70),
            ('Soy Sauce 1L', 25.00, 35),
        ]

        created = 0
        for name, price, qty in items_data:
            _, was = Item.objects.get_or_create(
                name=name, defaults={'price': price, 'qty': qty}
            )
            if was:
                created += 1

        self.stdout.write(f'Seeded {created} items')

        creditor, _ = Creditor.objects.get_or_create(
            name='Juan Dela Cruz',
            defaults={'contact_info': '09171234567'}
        )
        creditor2, _ = Creditor.objects.get_or_create(
            name='Maria Santos',
            defaults={'contact_info': '09281234567'}
        )
        self.stdout.write('Seeded 2 creditors')

        if Transaction.objects.count() == 0:
            coke = Item.objects.get(name='Coca-Cola')
            rice = Item.objects.get(name='Rice 1kg')
            coffee = Item.objects.get(name='Coffee 3in1')
            eggs = Item.objects.get(name='Eggs (per tray)')

            Transaction.objects.create(item=coke, transaction_type='sale', qty=3, total=75.00)
            Transaction.objects.create(item=rice, transaction_type='sale', qty=2, total=110.00)
            Transaction.objects.create(item=coffee, transaction_type='stock_in', qty=50, total=400.00)
            Transaction.objects.create(item=eggs, transaction_type='credit_sale', qty=1, total=210.00, creditor=creditor)
            Transaction.objects.create(item=coke, transaction_type='stock_in', qty=30, total=750.00)
            Transaction.objects.create(item=rice, transaction_type='stock_out', qty=5, total=275.00)
            Transaction.objects.create(item=coffee, transaction_type='sale', qty=10, total=80.00, creditor=creditor2)
            self.stdout.write('Seeded 7 sample transactions')

        self.stdout.write(self.style.SUCCESS('Done seeding!'))
