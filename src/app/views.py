from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Profile, TradeHistory, Stock, StockPrice
from .resources import TradeHistoryResource
from .forms import UserEditForm, ProfileEditForm, DateForm

import csv
import io
import requests


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
    date_form = DateForm()
    stock = Stock.objects.all()
    if request.method == 'POST':
        start_date = str(request.POST['start_date']).replace("-", "")
        end_date = str(request.POST['end_date']).replace("-", "")

        for field in stock:
            ticker = field.ticker
            download_url = f'https://stooq.com//q/d/l/?s={ticker}&d1={start_date}&d2={end_date}&i=d'
            req = requests.get(download_url)
            url_content = req.content.decode('UTF-8')
            io_string = io.StringIO(url_content)
            next(io_string)
            for row in csv.reader(io_string, delimiter=',', quotechar="|"):
                price_history = StockPrice(
                    date=row[0],
                    open=row[1],
                    high=row[2],
                    low=row[3],
                    close=row[4],
                    volume=row[5])
                price_history.save()

    return render(request, 'account/historical_price_update.html', {'date_form': date_form})
