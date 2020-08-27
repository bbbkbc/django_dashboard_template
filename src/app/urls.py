from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('edit/', views.edit_profile, name='edit'),
    path('charts/', views.charts, name='charts'),
    path('tables/', views.tables, name='tables'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
