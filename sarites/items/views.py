import json
from urllib.parse import urlparse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.template.loader import render_to_string
from .models import Item
from .forms import ItemForm
from .utils import import_items_from_excel, parse_nlp_input
from transactions.models import Transaction
from creditors.models import Creditor
from sarites.pagination import paginate


def item_list(request):
    query = request.GET.get('q', '')
    items = Item.objects.all()
    if query:
        items = items.filter(Q(name__icontains=query))
    items_page = paginate(items, request, param_name='page')
    return render(request, 'items/item_list.html', {'items': items_page, 'query': query})


def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                response = HttpResponse()
                response['HX-Trigger'] = 'dashboard-updated'
                return response
            return redirect('item_list')
    else:
        form = ItemForm()
    template = 'items/item_form_content.html' if request.headers.get('HX-Request') else 'items/item_form.html'
    return render(request, template, {'form': form})


def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                response = HttpResponse()
                response['HX-Trigger'] = 'dashboard-updated'
                return response
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    template = 'items/item_form_content.html' if request.headers.get('HX-Request') else 'items/item_form.html'
    return render(request, template, {'form': form, 'item': item})


def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        if request.headers.get('HX-Request'):
            current_url = request.headers.get('HX-Current-URL', '/')
            path = urlparse(current_url).path
            if path.startswith('/items/'):
                response = HttpResponse()
                response['HX-Location'] = current_url
                response['HX-Trigger'] = 'close-modal'
                return response
            items_page = paginate(
                Item.objects.annotate(tx_count=Count('transactions')).all(),
                request, param_name='items_page'
            )
            html = render_to_string('partials/_items_table.html', {'items': items_page}, request=request)
            response = HttpResponse(html)
            response['HX-Retarget'] = '#items-table'
            response['HX-Trigger'] = 'close-modal'
            return response
        return redirect('item_list')
    if request.headers.get('HX-Request'):
        return render(request, 'items/item_confirm_delete.html', {'item': item})
    return render(request, 'items/item_confirm_delete.html', {'item': item})


def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        result = import_items_from_excel(request.FILES['file'])
        return JsonResponse(result)
    return JsonResponse({'error': 'No file provided'}, status=400)


def public_items(request):
    q = request.GET.get('q', '')
    items = Item.objects.all()
    if q:
        items = items.filter(name__icontains=q)
    return render(request, 'items/public_items.html', {'items': items, 'query': q})


def item_suggest(request):
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
    items = Item.objects.filter(name__icontains=q).values('id', 'name', 'price', 'qty')[:8]
    return JsonResponse(list(items), safe=False)


def nlp_search(request):
    text = request.GET.get('q', '')
    parsed = parse_nlp_input(text)
    if not parsed:
        return JsonResponse({'match': False})

    name = parsed['name'].strip().title()
    match = Item.objects.filter(name__iexact=name).first()

    creditor_data = None
    if parsed.get('creditor'):
        name = parsed['creditor'].strip().title()
        creditor = Creditor.objects.filter(name__iexact=name).first()
        if creditor:
            creditor_data = {'id': creditor.id, 'name': creditor.name}

    if match:
        total = float(match.price) * parsed['qty']
        reduces_stock = parsed['transaction_type'] in ('sale', 'credit_sale', 'stock_out')
        low_stock = reduces_stock and match.qty < parsed['qty']
        return JsonResponse({
            'match': True,
            'transaction_type': parsed['transaction_type'],
            'item': {
                'id': match.id,
                'name': match.name,
                'price': float(match.price),
                'qty': parsed['qty'],
                'total': total,
            },
            'creditor': creditor_data,
            'low_stock': low_stock,
            'available': match.qty,
        })
    suggested_price = parsed.get('unit_price')
    return JsonResponse({
        'match': False,
        'is_new_item': True,
        'parsed_name': parsed['name'],
        'qty': parsed['qty'],
        'transaction_type': parsed['transaction_type'],
        'suggested_price': suggested_price,
        'creditor': creditor_data,
    })
