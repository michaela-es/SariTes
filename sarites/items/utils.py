import pandas as pd
from .models import Item


def import_items_from_excel(file):
    df = pd.read_excel(file)
    required = {'name', 'price', 'qty'}
    missing = required - set(df.columns.str.lower())
    if missing:
        return {'error': f'Missing columns: {", ".join(sorted(missing))}'}

    df.columns = df.columns.str.lower()
    created = 0
    updated = 0
    errors = []

    for _, row in df.iterrows():
        try:
            name = str(row['name']).strip()
            price = float(row['price'])
            qty = int(row['qty'])
            item, was_created = Item.objects.get_or_create(
                name__iexact=name,
                defaults={'name': name, 'price': price, 'qty': qty},
            )
            if not was_created:
                item.price = price
                item.qty += qty
                item.save()
                updated += 1
            else:
                created += 1
        except Exception as e:
            errors.append(f"Row {row.name}: {e}")

    return {'created': created, 'updated': updated, 'errors': errors, 'total': len(df)}


def parse_nlp_input(text):
    parts = text.strip().split(None, 1)
    if not parts:
        return None
    try:
        qty = int(parts[0])
        rest = parts[1] if len(parts) > 1 else ''
    except (ValueError, IndexError):
        qty = 1
        rest = text.strip()

    name = rest.strip()
    if not name:
        return None

    creditor = None
    if '@' in name:
        name, _, creditor = name.partition('@')
        creditor = creditor.strip()

    return {'qty': qty, 'name': name.strip(), 'creditor': creditor}
