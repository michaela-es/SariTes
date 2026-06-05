from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Creditor
from .forms import CreditorForm
from transactions.models import Transaction
from sarites.pagination import paginate


def creditor_list(request):
    return redirect('dashboard')


def creditor_create(request):
    if request.method == 'POST':
        form = CreditorForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Trigger'] = 'dashboard-updated, close-modal'
                return response
            return redirect('dashboard')
    else:
        form = CreditorForm()
    template = 'creditors/creditor_form_content.html' if request.headers.get('HX-Request') else 'creditors/creditor_form.html'
    return render(request, template, {'form': form})


def creditor_edit(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    if request.method == 'POST':
        form = CreditorForm(request.POST, instance=creditor)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Trigger'] = 'dashboard-updated, close-modal'
                return response
            return redirect('dashboard')
    else:
        form = CreditorForm(instance=creditor)
    template = 'creditors/creditor_form_content.html' if request.headers.get('HX-Request') else 'creditors/creditor_form.html'
    return render(request, template, {'form': form, 'creditor': creditor})


def creditor_delete(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    if request.method == 'POST':
        creditor.delete()
        return redirect('dashboard')
    return render(request, 'creditors/creditor_confirm_delete.html', {'creditor': creditor})


def creditor_detail(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    transactions = Transaction.objects.filter(creditor=creditor, transaction_type='credit_sale').select_related('item').order_by('-created_at')
    transactions_page = paginate(transactions, request, param_name='page')
    return render(request, 'creditors/creditor_detail.html', {
        'creditor': creditor,
        'transactions': transactions_page,
    })
