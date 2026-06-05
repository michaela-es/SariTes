from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('dashboard-partials/', views.dashboard_partials, name='dashboard_partials'),
    path('', include('items.urls')),
    path('', include('transactions.urls')),
    path('', include('creditors.urls')),
    path('analytics-data/', views.analytics_data, name='analytics_data'),
]
