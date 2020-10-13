from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import StockPrice, TradeHistory, Stock
from .models import Pnl
from .forms import DateForm
import queue
from django.utils.timezone import now
from datetime import timedelta



@login_required
def pnl(request):
    pnl_obj = Pnl
    date_form = DateForm(request.POST or None)
    buy_queue = queue.Queue()
    lst_k = []

    if date_form.is_valid():
        eval_date = request.POST['evaluation_date']
        stock_base = Stock.objects.all()
        for stock_name in stock_base:
            trade_history = TradeHistory.objects.all().filter(
                date_time__lte=eval_date).order_by(
                'date_time').filter(stock=stock_name)
            for item in trade_history:
                if item.site == 'K':
                    lst_k.append(item)
            start_date = trade_history[0].date_time.date()

            end_date = now().date()
            days_number = int((end_date-start_date).days)
            pnl_k = 0
            pnl_s = 0
            # for n in range(days_number):
            #     evaluation_day = start_date + timedelta(n)
            #     price_history = StockPrice.objects.all().filter(stock=stock_name).filter(date=evaluation_day)
            #     for item in trade_history:
            #         for record in price_history:
            #             if item.site == 'K':
            #                 diff_k = record.close - item.stock_price
            #                 pnl_k = round(item.num_of_share * diff_k, ndigits=2)
            #             elif item.site == 'S':
            #                 diff_s = record.close - item.stock_price
            #                 pnl_s = round(item.num_of_share * diff_s, ndigits=2)
    print(lst_k)
    # stock_price
    # num_of_share
    # site
    # stock
    context = {'date_form': date_form}
    return render(request, 'account/pnl.html', context)
