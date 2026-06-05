from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/new/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('transactions/<int:pk>/mark-paid/', views.mark_paid, name='mark_paid'),
    path('creditors/<int:creditor_id>/mark-all-paid/', views.mark_all_paid, name='mark_all_paid'),
    path('quick-sale/', views.quick_sale, name='quick_sale'),
    path('transactions/export/', views.transaction_export, name='transaction_export'),
]
