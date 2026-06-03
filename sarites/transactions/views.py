import json
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Transaction
from .forms import TransactionForm
from items.models import Item
from items.utils import parse_nlp_input


@login_required
def transaction_list(request):
    ttype = request.GET.get('type', '')
    q = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    today = timezone.now().date()
    transactions = Transaction.objects.select_related('item', 'creditor').all()

    if date_filter == 'today':
        transactions = transactions.filter(created_at__date=today)
    elif date_filter == 'week':
        week_start = today - timedelta(days=today.weekday())
        transactions = transactions.filter(created_at__date__gte=week_start)
    elif date_filter == 'month':
        month_start = today.replace(day=1)
        transactions = transactions.filter(created_at__date__gte=month_start)
    elif date_from and date_to:
        transactions = transactions.filter(
            created_at__date__gte=date_from, created_at__date__lte=date_to
        )

    if ttype:
        transactions = transactions.filter(transaction_type=ttype)
    if q:
        transactions = transactions.filter(Q(item__name__icontains=q) | Q(notes__icontains=q))
    totals = transactions.aggregate(total_sum=Sum('total'))
    return render(request, 'transactions/transaction_list.html', {
        'transactions': transactions,
        'totals': totals,
        'filter_type': ttype,
        'query': q,
        'date_filter': date_filter,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    template = 'transactions/transaction_form_content.html' if request.headers.get('HX-Request') else 'transactions/transaction_form.html'
    return render(request, template, {'form': form})


@login_required
def quick_sale(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        parsed = parse_nlp_input(data.get('text', ''))
        if not parsed:
            return JsonResponse({'error': 'Could not parse input'}, status=400)

        items = Item.objects.filter(name__icontains=parsed['name'])
        if not items.exists():
            return JsonResponse({'error': f'No item matching "{parsed["name"]}"'}, status=400)

        item = items.first()
        creditor = None
        ttype = parsed.get('transaction_type', 'sale')
        if parsed.get('creditor'):
            from creditors.models import Creditor
            creditor = Creditor.objects.filter(name__icontains=parsed['creditor']).first()
            if creditor and ttype == 'sale':
                ttype = 'credit_sale'

        total = float(item.price) * parsed['qty']
        transaction = Transaction.objects.create(
            item=item,
            transaction_type=ttype,
            qty=parsed['qty'],
            total=total,
            creditor=creditor,
        )

        return JsonResponse({
            'id': transaction.id,
            'item': item.name,
            'qty': parsed['qty'],
            'total': total,
            'type': ttype,
        })
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transaction})


@login_required
def mark_paid(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, transaction_type='credit_sale')
    if request.method == 'POST':
        transaction.transaction_type = 'sale'
        transaction.save(update_fields=['transaction_type'])
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def mark_all_paid(request, creditor_id):
    if request.method == 'POST':
        count = Transaction.objects.filter(
            creditor_id=creditor_id, transaction_type='credit_sale'
        ).update(transaction_type='sale')
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'error': 'POST required'}, status=405)
