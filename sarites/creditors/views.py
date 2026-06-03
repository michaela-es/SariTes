from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from .models import Creditor
from .forms import CreditorForm
from transactions.models import Transaction


@login_required
def creditor_list(request):
    return redirect('dashboard')


@login_required
def creditor_create(request):
    if request.method == 'POST':
        form = CreditorForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
            return redirect('dashboard')
    else:
        form = CreditorForm()
    template = 'creditors/creditor_form_content.html' if request.headers.get('HX-Request') else 'creditors/creditor_form.html'
    return render(request, template, {'form': form})


@login_required
def creditor_edit(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    if request.method == 'POST':
        form = CreditorForm(request.POST, instance=creditor)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
            return redirect('dashboard')
    else:
        form = CreditorForm(instance=creditor)
    template = 'creditors/creditor_form_content.html' if request.headers.get('HX-Request') else 'creditors/creditor_form.html'
    return render(request, template, {'form': form, 'creditor': creditor})


@login_required
def creditor_delete(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    if request.method == 'POST':
        creditor.delete()
        return redirect('dashboard')
    return render(request, 'creditors/creditor_confirm_delete.html', {'creditor': creditor})


@login_required
def creditor_detail(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    transactions = Transaction.objects.filter(creditor=creditor, transaction_type='credit_sale').select_related('item').order_by('-created_at')
    return render(request, 'creditors/creditor_detail.html', {
        'creditor': creditor,
        'transactions': transactions,
    })
