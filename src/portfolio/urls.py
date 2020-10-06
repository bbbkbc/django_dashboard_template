from django.urls import path
from . import views


urlpatterns = [
    path('pnl/', views.pnl, name='pnl'),
]
