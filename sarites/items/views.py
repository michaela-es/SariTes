import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Item
from .forms import ItemForm
from .utils import import_items_from_excel, parse_nlp_input
from transactions.models import Transaction
from creditors.models import Creditor


@login_required
def item_list(request):
    query = request.GET.get('q', '')
    items = Item.objects.all()
    if query:
        items = items.filter(Q(name__icontains=query))
    return render(request, 'items/item_list.html', {'items': items, 'query': query})


@login_required
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


@login_required
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


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'items/item_confirm_delete.html', {'item': item})


@login_required
def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        result = import_items_from_excel(request.FILES['file'])
        return JsonResponse(result)
    return JsonResponse({'error': 'No file provided'}, status=400)


@login_required
def item_suggest(request):
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse([], safe=False)
    items = Item.objects.filter(name__icontains=q).values('id', 'name', 'price', 'qty')[:8]
    return JsonResponse(list(items), safe=False)


@login_required
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
        })
    return JsonResponse({
        'match': False,
        'parsed_name': parsed['name'],
        'transaction_type': parsed['transaction_type'],
        'creditor': creditor_data,
    })
