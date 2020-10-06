from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime, timedelta


from .models import Profile, TradeHistory, Stock, StockPrice
from .resources import TradeHistoryResource
from .forms import UserEditForm, ProfileEditForm, DateForm, TradeForm, FilterForm, ChartsForm

import csv
import io
import requests
import pandas as pd
import operator


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        else:
            user_form = UserEditForm()
            return render(request, 'account/edit.html', {'user_form': user_form})
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    messages.success(request, 'You successfully enter changes to your profile')
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def tables(request):
    return render(request, 'account/tables.html')


@login_required
def trades(request):
    try:
        user = request.user
        user_id = Profile.objects.get(user=user)
    except:
        Profile.objects.get_or_create(user=request.user)
        return redirect(edit_profile)

    if request.method == 'POST':
        try:
            csv_file = request.FILES['importData']
        except MultiValueDictKeyError:
            messages.warning(request, 'First you have to pick a file!')
            return render(request, 'account/trade_utility.html')
        if not csv_file.name.endswith('.csv'):
            messages.warning(request, 'You try to import file which has different extension than .csv')
            return render(request, 'account/trade_utility.html')
        new_trades = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(new_trades)
        next(io_string)
        for col in csv.reader(io_string, delimiter=',', quotechar="|"):
            try:
                stock_id = Stock.objects.get(symbol=col[1])
            except:
                messages.warning(request, f"Stock which cause an error {col[1]}, "
                                          f"Please contact with admin, we don't have this stock in our base")
                return render(request, 'account/trade_utility.html')
            trade_history = TradeHistory(user=user_id,
                                         stock=stock_id,
                                         date_time=col[0],
                                         name=col[1],
                                         site=col[2],
                                         num_of_share=col[3],
                                         stock_price=col[4],
                                         value=col[5])
            trade_history.save()
        messages.success(request, 'Data Base update completed!')
    return render(request, 'account/trade_utility.html')


@login_required
def add_new_trade(request):
    form = TradeForm(request.POST or None)

    if form.is_valid():
        form.save()
        form = TradeForm()

    trade_history = TradeHistory.objects.all().order_by('-date_time')[:10]
    context = {'form': form,
               'trade_tab': trade_history}
    return render(request, 'account/add_new_trade.html', context)


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
    date_form = DateForm(request.POST or None)
    stock = Stock.objects.all()
    if date_form.is_valid():
        start_date = str(request.POST['start_date']).replace("-", "")
        end_date = str(request.POST['end_date']).replace("-", "")
        for field in stock:
            try:
                last_record = StockPrice.objects.filter(stock=field).latest('date')
                delta = timedelta(days=1)
                start_date = str(last_record.date + delta).replace("-", "")
            except StockPrice.DoesNotExist:
                print(field, 'no in db')
            finally:
                ticker = field.ticker
                stock_id = Stock.objects.get(ticker=ticker)
                download_url = f'https://stooq.com//q/d/l/?s={ticker}&d1={start_date}&d2={end_date}&i=d'
                req = requests.get(download_url)
                url_content = req.content.decode('UTF-8')
                io_string = io.StringIO(url_content)
                next(io_string)
                counter = 0
                for row in csv.reader(io_string, delimiter=',', quotechar="|"):
                    if counter == 0:
                        print(ticker, row)
                        counter += 1

                    price_history = StockPrice(
                        stock=stock_id,
                        date=row[0],
                        open=row[1],
                        high=row[2],
                        low=row[3],
                        close=row[4],
                        volume=row[5])
                    price_history.save()

    filter_form = FilterForm(request.POST or None)

    if filter_form.is_valid():

        filter_date = request.POST.get('filter_date')
        filter_date_dt = datetime.strptime(filter_date, '%Y-%m-%d').date()
        last_date = StockPrice.objects.filter().latest('date').date

        if filter_date_dt > last_date:
            filter_date = last_date
            messages.warning(request, 'You try to reach unavailable date')

    else:
        filter_date = '2020-09-23'

    stock_price = StockPrice.objects.all().filter(stock__in=stock).filter(date=filter_date)
    stock_price2 = StockPrice.objects.all().filter(stock__in=stock).filter(date=filter_date).values()

    df = pd.DataFrame(stock_price)
    df2 = pd.DataFrame(stock_price2)
    df2['name'] = df
    df2 = df2[['name', 'date', 'close']]
    context = {'date_form': date_form,
               'filter_form': filter_form,
               'stock': stock,
               'df2': df2.to_html()}
    return render(request, 'account/historical_price_update.html', context)


def stock_chart(request):
    labels = []
    volume = []
    data = []
    date_form = DateForm(request.POST or None)
    charts_form = ChartsForm(request.POST or None)
    filter_price = 'open'
    if request.method == 'POST':

        if date_form.is_valid():
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

        if charts_form.is_valid():
            filter_stock = request.POST.get('stock')
            filter_price = request.POST.get('price')
            stock_name = Stock.objects.get(id=filter_stock).symbol
            stock_info = Stock.objects.get(id=filter_stock)
        qs = StockPrice.objects.all().filter(
            stock=filter_stock).filter(
            date__range=[start_date, end_date]).order_by('date')
    else:
        stock_info = Stock.objects.get(id=0)
        stock_name = 'TAURONPE'
        qs = StockPrice.objects.all().filter(stock=0).order_by('date')

    stock_obj = Stock.objects.all()
    perfomance_dict = {}

    for element in stock_obj:
        stock_price_first = StockPrice.objects.filter(stock=element).order_by('-date')[10]
        stock_price_last = StockPrice.objects.filter(stock=element).order_by('-date')[0]
        price_return = ((stock_price_last.close -
                         stock_price_first.close) / ((stock_price_last.close +
                                                      stock_price_first.close)/2))*100
        perfomance_dict[element] = round(price_return, ndigits=2)
    sorted_dict = (sorted(perfomance_dict.items(), key=operator.itemgetter(1), reverse=True))
    worst_5 = sorted_dict[-5:]
    best_5 = sorted_dict[:5]

    for item in qs:
        volume.append(item.volume)
        labels.append(item.date.strftime('%m/%d'))
        if filter_price == 'open':
            data.append(item.open)
        elif filter_price == 'high':
            data.append(item.high)
        elif filter_price == 'low':
            data.append(item.low)
        elif filter_price == 'close':
            data.append(item.close)

    context = {'date_form': date_form,
               'charts_form': charts_form,
               'labels': labels,
               'data': data,
               'symbol': stock_name,
               'stock_info': stock_info,
               'volume': volume,
               'best': best_5,
               'worst': worst_5}
    return render(request, 'account/stock_chart.html', context)
