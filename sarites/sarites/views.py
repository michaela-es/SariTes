import json
from datetime import date, timedelta, datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from transactions.models import Transaction
from creditors.models import Creditor
from items.models import Item


@login_required
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

    selected_creditor = request.GET.get('creditor', '')
    creditor_detail = None
    if selected_creditor:
        creditor_detail = Creditor.objects.filter(id=selected_creditor).first()

    return render(request, 'dashboard.html', {
        'recent': recent,
        'transactions': txs,
        'creditors': creditors,
        'items': items,
        'creditor_detail': creditor_detail,
        'selected_creditor': selected_creditor,
        'date_filter': date_filter,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def analytics_data(request):
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    trans = Transaction.objects.filter(created_at__gte=since)
    sales = trans.filter(transaction_type__in=['sale', 'credit_sale'])
    stocks = trans.filter(transaction_type__in=['stock_in', 'stock_out'])

    daily_sales = []
    for i in range(days):
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
