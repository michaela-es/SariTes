from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Creditor
from .forms import CreditorForm


@login_required
def creditor_list(request):
    q = request.GET.get('q', '')
    creditors = Creditor.objects.all()
    if q:
        creditors = creditors.filter(Q(name__icontains=q) | Q(contact_info__icontains=q))
    return render(request, 'creditors/creditor_list.html', {'creditors': creditors, 'query': q})


@login_required
def creditor_create(request):
    if request.method == 'POST':
        form = CreditorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('creditor_list')
    else:
        form = CreditorForm()
    return render(request, 'creditors/creditor_form.html', {'form': form})


@login_required
def creditor_edit(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    if request.method == 'POST':
        form = CreditorForm(request.POST, instance=creditor)
        if form.is_valid():
            form.save()
            return redirect('creditor_list')
    else:
        form = CreditorForm(instance=creditor)
    return render(request, 'creditors/creditor_form.html', {'form': form, 'creditor': creditor})


@login_required
def creditor_delete(request, pk):
    creditor = get_object_or_404(Creditor, pk=pk)
    if request.method == 'POST':
        creditor.delete()
        return redirect('creditor_list')
    return render(request, 'creditors/creditor_confirm_delete.html', {'creditor': creditor})
