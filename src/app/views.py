from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from .models import Profile


@login_required
def dashboard(request):
    return render(request,'account/dashboard.html',)


@login_required
def edit_profile(request):
    return render(request, 'account/edit.html')


@login_required
def charts(request):
    return render(request, 'account/charts.html')
