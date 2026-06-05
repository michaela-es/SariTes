# SariTes

A Django inventory management system built for sari-sari stores, evolved from the **CSIT327-G1-InnoVentory** project.

> **Single-tenant** — not designed for multi-store or multi-user use. Intended for one sari-sari store operated by the owner.
>
> **Testing status** — user testing currently underway, conducted personally by the developer.

## Key Difference: NLP Quick Entry

Unlike Innoventory's traditional form-based transaction logging, SariTes uses a **pattern-based natural language command interface** for faster, more intuitive logging:

```
5 Coke          → sell 5 Coke (defaults to Sale)
+10 Rice        → stock in 10 Rice
-3 Sardines     → stock out 3 Sardines
2 Coffee @Juan  → sell 2 Coffee on credit to Juan
```

This reduces a multi-click form to a single text entry, making day-to-day operations faster and more familiar for store owners.

## Features

- **Quick Entry** — natural language transaction logging with autocomplete
- **Items** — product catalog with stock level tracking and Excel import
- **Transactions** — full transaction history with date/type filtering
- **Creditors** — credit sale tracking with Mark Paid / Mark All Paid
- **Analytics** — Chart.js dashboards for sales trends, top items, and creditor balances
- **Mobile responsive** — works on phones and tablets
- **HTMX modals** — all CRUD forms in modals, no page reloads

## Tech Stack

- Django 5
- SQLite / PostgreSQL (via Supabase)
- Tailwind CSS (CDN)
- HTMX
- Chart.js
- Bootstrap Icons

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed                          # sample data
python manage.py createsuperuser --username admin  # create login credentials
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and log in with the superuser credentials.

For Supabase: copy `.env.example` → `.env`, fill in `DATABASE_URL`, then `python manage.py migrate`.
