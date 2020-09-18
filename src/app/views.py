from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, TradeHistory, Stock, StockPrice
from .resources import TradeHistoryResource
from django.http import HttpResponse
import csv
import io
import requests



@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')


@login_required
def edit_profile(request):
    try:
        profile = Profile.objects.get(user=user)
    except:
        profile = 'Profile does not exist'
    context = {'profile': profile}

    return render(request, 'account/edit.html', context)


@login_required
def charts(request):
    return render(request, 'account/charts.html')


@login_required
def tables(request):
    return render(request, 'account/tables.html')


@login_required
def trades(request):
    try:
        user = request.user
        user_id = Profile.objects.get(user=user)
    except:
        return redirect(edit_profile)
    if request.method == 'POST':
        csv_file = request.FILES['importData']
        if not csv_file.name.endswith('.csv'):
            print("wrong file type")
        new_trades = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(new_trades)
        next(io_string)
        for col in csv.reader(io_string, delimiter=',', quotechar="|"):
            try:
                stock_id = Stock.objects.get(symbol=col[1])
            except:
                print('There is no such stock in database:', col[1])
            trade_history = TradeHistory(user=user_id,
                                         stock=stock_id,
                                         date_time=col[0],
                                         name=col[1],
                                         site=col[2],
                                         num_of_share=col[3],
                                         stock_price=col[4],
                                         value=col[5])
            trade_history.save()

    return render(request, 'account/trade_utility.html')


@login_required
def export_data(request):
    user_id = request.user.id
    trade_history = TradeHistoryResource()
    queryset = TradeHistory.objects.all().filter(user_id=user_id)
    dataset = trade_history.export(queryset)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment: filename=trade_history.csv'
    return response


@login_required
def sync(request):
    # in progress
    stock = Stock.objects.all()
    start_date = '20200101'
    end_date = '20200901'
    for field in stock:
        ticker = field.ticker
        download_url = f'https://stooq.com//q/d/l/?s={ticker}&d1={start_date}&d2={end_date}&i=d'
        req = requests.get(download_url)
        url_content = req.content.decode('UTF-8')
        io_string = io.StringIO(url_content)
        next(io_string)
    return render(request, 'account/dashboard.html')
