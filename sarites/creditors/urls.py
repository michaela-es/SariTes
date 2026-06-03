from django.urls import path
from . import views

app_name = 'creditors'

urlpatterns = [
    path('creditors/', views.creditor_list, name='creditor_list'),
    path('creditors/new/', views.creditor_create, name='creditor_create'),
    path('creditors/<int:pk>/edit/', views.creditor_edit, name='creditor_edit'),
    path('creditors/<int:pk>/delete/', views.creditor_delete, name='creditor_delete'),
    path('creditors/<int:pk>/', views.creditor_detail, name='creditor_detail'),
]
