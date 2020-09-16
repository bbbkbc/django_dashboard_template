from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile, TradeHistory
from .resources import TradeHistoryResource
from django.http import HttpResponse


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')


@login_required
def edit_profile(request):
    context = {'profile': Profile.objects.all()}

    return render(request, 'account/edit.html', context)


@login_required
def charts(request):
    return render(request, 'account/charts.html')


@login_required
def tables(request):
    return render(request, 'account/tables.html')


@login_required
def trades(request):
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
