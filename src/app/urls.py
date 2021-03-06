from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('edit/', views.edit_profile, name='edit'),
    path('stock_chart/', views.stock_chart, name='stock_chart'),
    path('tables/', views.tables, name='tables'),
    path('trades/', views.trades, name='trades'),
    path('sync/', views.sync, name='sync'),
    path('export_data/', views.export_data, name='export_data'),
    path('add_new_trade/', views.add_new_trade, name='add_new_trade'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
