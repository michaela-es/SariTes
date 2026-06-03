import json
from datetime import date, timedelta, datetime
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone
from transactions.models import Transaction
from creditors.models import Creditor
from items.models import Item


def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    date_filter = request.GET.get('date', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    txs = Transaction.objects.select_related('item', 'creditor').all()
    if date_filter == 'today':
        txs = txs.filter(created_at__date=today)
    elif date_filter == 'week':
        txs = txs.filter(created_at__date__gte=week_ago)
    elif date_filter == 'month':
        txs = txs.filter(created_at__date__gte=month_start)
    elif date_from and date_to:
        txs = txs.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)

    recent = Transaction.objects.select_related('item', 'creditor').all()[:10]
    creditors = Creditor.objects.annotate(tx_count=Count('transactions')).all()
    items = Item.objects.annotate(tx_count=Count('transactions')).all()

    today_sales = Transaction.objects.filter(
        transaction_type='sale',
        created_at__date=today,
    ).aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'dashboard.html', {
        'recent': recent,
        'transactions': txs,
        'creditors': creditors,
        'items': items,
        'today_sales': today_sales,
        'date_filter': date_filter,
        'date_from': date_from,
        'date_to': date_to,
    })


def analytics_data(request):
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    trans = Transaction.objects.filter(created_at__gte=since)
    sales = trans.filter(transaction_type__in=['sale', 'credit_sale'])
    stocks = trans.filter(transaction_type__in=['stock_in', 'stock_out'])

    daily_sales = []
    for i in range(days + 1):
        day = (since + timedelta(days=i)).date()
        total = sales.filter(created_at__date=day).aggregate(s=Sum('total'))['s'] or 0
        daily_sales.append({'date': day.isoformat(), 'total': float(total)})

    by_type = list(trans.values('transaction_type').annotate(
        total=Sum('total'), count=Count('id')
    ))

    top_items = list(
        trans.values('item__name').annotate(
            total=Sum('total'), count=Count('id')
        ).order_by('-total')[:10]
    )

    creditor_balances = list(
        Creditor.objects.annotate(
            balance=Sum('transactions__total', filter=Q(transactions__transaction_type='credit_sale'))
        ).values('name', 'balance')
    )

    return JsonResponse({
        'daily_sales': daily_sales,
        'by_type': by_type,
        'top_items': top_items,
        'creditor_balances': creditor_balances,
    })


def dashboard_partials(request):
    today = timezone.now().date()
    sections = []
    for s in request.GET.getlist('sections'):
        sections.extend([x.strip() for x in s.split(',') if x.strip()])

    date_filter = request.GET.get('date', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    txs = Transaction.objects.select_related('item', 'creditor').all()
    if date_filter == 'today':
        txs = txs.filter(created_at__date=today)
    elif date_filter == 'week':
        txs = txs.filter(created_at__date__gte=today - timedelta(days=today.weekday()))
    elif date_filter == 'month':
        txs = txs.filter(created_at__date__gte=today.replace(day=1))
    elif date_from and date_to:
        txs = txs.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)

    context = {
        'recent': Transaction.objects.select_related('item', 'creditor').all()[:10],
        'transactions': txs,
        'items': Item.objects.annotate(tx_count=Count('transactions')).all(),
        'creditors': Creditor.objects.annotate(tx_count=Count('transactions')).all(),
        'today_sales': Transaction.objects.filter(
            transaction_type='sale', created_at__date=today,
        ).aggregate(total=Sum('total'))['total'] or 0,
        'date_filter': date_filter,
        'date_from': date_from,
        'date_to': date_to,
    }

    html = {}
    for s in sections:
        s = s.strip()
        if s == 'stats':
            html['stats-cards'] = render_to_string('partials/_stats_cards.html', context, request=request)
        elif s == 'recent':
            html['recent-txns'] = render_to_string('partials/_transaction_table.html', {
                **context,
                'title': '<i class="bi bi-clock-history"></i> Recent Transactions',
                'transactions': context['recent'],
                'show_creditor': True,
                'show_actions': False,
                'show_status': False,
                'empty_message': 'No transactions yet. Try a quick entry above!',
            }, request=request)
        elif s == 'txns':
            html['txns-table'] = render_to_string('partials/_transaction_table.html', {
                **context,
                'transactions': txs,
                'show_creditor': True,
                'show_actions': True,
                'show_status': False,
                'empty_message': 'No transactions in this period.',
                'max_height': '60vh',
            }, request=request)
        elif s == 'items':
            html['items-table'] = render_to_string('partials/_items_table.html', context, request=request)
        elif s == 'creditors':
            html['creditors-table'] = render_to_string('partials/_creditors_table.html', context, request=request)

    return JsonResponse(html)
