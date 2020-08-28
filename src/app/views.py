from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from .admin import StockResource, TradeHistoryResource
from tablib import Dataset
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from .models import TradeHistory


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html',)


@login_required
def edit_profile(request):
    return render(request, 'account/edit.html')


@login_required
def charts(request):
    return render(request, 'account/charts.html')


@login_required
def tables(request):
    return render(request, 'account/tables.html')


@login_required
def import_export(request):
    return render(request, 'account/stock_data.html')


def export_data(request):
    stock_resource = StockResource()
    dataset = stock_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment: filename=stocks.csv'
    return response


def import_data(request):
    if request.method == 'POST':
        stocks_resource = StockResource()
        dataset = Dataset()
        try:
            new_stocks = request.FILES['importData']
        except MultiValueDictKeyError:
            messages.warning(request, 'Firstly you have to pick a file!')
            return render(request, 'secret_page.html')
        imported_data = dataset.load(new_stocks.read().decode('utf-8'), format='csv')
        result = stocks_resource.import_data(dataset, dry_run=True)
        if not result.has_errors():
            # Import now
            messages.success(request, 'Upload done successfully!')
            stocks_resource.import_data(dataset, dry_run=False)
        else:
            messages.warning(request, 'Data is already in database!')
            return render(request, 'secret_page.html')

    return render(request, 'secret_page.html')


def export_trade(request):
    trade_resource = TradeHistoryResource()
    dataset = trade_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment: filename=stocks.csv'
    return response


def import_trade_history(request):
    if request.method == 'POST':
        trade_resource = TradeHistoryResource()
        dataset = Dataset()
        try:
            new_trades = request.FILES['importData']
        except MultiValueDictKeyError:
            messages.warning(request, 'Firstly you have to pick a file!')
            return render(request, 'secret_page.html')
        imported_data = dataset.load(new_trades.read().decode('utf-8'), format='csv')
        result = trade_resource.import_data(dataset, dry_run=True)
        if not result.has_errors():
            # Import now
            messages.success(request, 'Upload done successfully!')
            trade_resource.import_data(dataset, dry_run=False)
        else:
            messages.warning(request, 'Data is already in database!')
            return render(request, 'secret_page.html')

    return render(request, 'secret_page.html')


