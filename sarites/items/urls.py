from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    path('items/', views.item_list, name='item_list'),
    path('item/new/', views.item_create, name='item_create'),
    path('item/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('item/<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('nlp-search/', views.nlp_search, name='nlp_search'),
    path('item-suggest/', views.item_suggest, name='item_suggest'),
]
