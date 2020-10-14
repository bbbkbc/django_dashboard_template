from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import StockPrice, TradeHistory, Stock
from .models import Pnl
from .forms import DateForm
from datetime import timedelta, datetime
import pandas as pd


@login_required
def pnl(request):
    date_form = DateForm(request.POST or None)
    df_pnl_u = pd.DataFrame(columns=['date', 'pnl_u', 'stock_name', 'stock_id'])
    if date_form.is_valid():
        eval_date = request.POST['evaluation_date']
        end_date = datetime.strptime(eval_date, '%Y-%m-%d').date()
        stock_base = Stock.objects.all()
        for stock_name in stock_base:
            trade_history = TradeHistory.objects.all().filter(
                date_time__lte=eval_date).order_by(
                'date_time').filter(stock=stock_name)

            try:
                start_date = trade_history[0].date_time.date()
            except IndexError:
                print('queryset empty')
                continue

            buy_trades = []
            sell_trades = []
            for trade in trade_history:
                if trade.site == 'K':
                    buy_trades.append(trade)
                else:
                    sell_trades.append(trade)

            # unrealized pnl
            if len(sell_trades) == 0:
                for item in buy_trades:
                    item_date = item.date_time.date()
                    days_number = int((end_date - item_date).days)
                    for n in range(days_number):
                        evaluation_day = item_date + timedelta(n)
                        price_history = StockPrice.objects.all().filter(stock=stock_name).filter(date=evaluation_day)
                        try:
                            close_price = price_history[0].close
                            pnl_unrealized = (close_price - item.stock_price) * item.num_of_share
                            # print(evaluation_day, round(pnl_unrealized, ndigits=2), stock_name, item.id)
                            df_pnl_u = df_pnl_u.append({'date': evaluation_day,
                                                        'pnl_u': round(pnl_unrealized, ndigits=2),
                                                        'stock_name': stock_name,
                                                        'stock_id': item.id}, ignore_index=True
                                                       )
                        except IndexError:
                            continue
                            # print(evaluation_day, 'no price')

    # print(df_pnl_u)

    # stock_price
    # num_of_share
    # site
    # stock
    context = {'date_form': date_form}
    return render(request, 'account/pnl.html', context)
