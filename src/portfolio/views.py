from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import StockPrice, TradeHistory, Stock, Profile
from .models import Pnl, Fifo
from .forms import DateForm
from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import queue


@login_required
def pnl(request):
    try:
        user = request.user
        user_id = Profile.objects.get(user=user)
    except:
        print('no user id')
    date_form = DateForm(request.POST or None)

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

            # unpack queries
            trades = []
            for trade in trade_history:
                if trade.site == 'K':
                    trades.append(
                        [trade.date_time.date(),
                         trade.stock_price,
                         trade.num_of_share,
                         'buy'])
                else:
                    trades.append(
                        [trade.date_time.date(),
                         trade.stock_price,
                         trade.num_of_share,
                         'sell'])

            deals = pd.DataFrame(data=trades[:], columns=['date', 'price', 'quantity', 'side'])
            deals['deal_id'] = deals.index
            mtm_lst = []

            for trade in deals.itertuples():
                trade_date = trade.date
                days_number = int((end_date - trade_date).days)
                for n in range(days_number):
                    try:
                        date = trade_date + timedelta(n)

                        price_history = StockPrice.objects.all().filter(stock=stock_name).filter(date=date)

                        price = trade.price
                        quantity = trade.quantity
                        mkt_price = price_history[0].close
                        mtm = (mkt_price - price) * quantity
                        trade_id = trade.deal_id
                        side = trade.side
                        mtm_lst.append([date, price, quantity, mkt_price, mtm, trade_id, side])
                    except IndexError:
                        continue
            deals_mtm = pd.DataFrame(mtm_lst, columns=[
                'date',
                'price',
                'quantity',
                'mkt_price',
                'mtm',
                'trade_id',
                'side'])
            deals_mtm = deals_mtm.sort_values(['date', 'trade_id'])
            deals_mtm = deals_mtm.groupby(deals_mtm['date'])

            for deal in deals_mtm:
                buy_lst = []
                sell_lst = []
                for d in deal[1].itertuples():
                    eval_date = d.date
                    mkt_price = d.mkt_price
                    if d.side == 'buy':
                        buy_lst.append([d.quantity, d.mtm])
                    elif d.side == 'sell':
                        sell_lst.append([d.quantity, d.mtm])
                fifo = Fifo(buy_lst, sell_lst).run()
                print(user_id, stock_name, eval_date,  mkt_price, fifo)
                pnl_model = Pnl(
                    user=user_id,
                    stock=stock_name,
                    date=eval_date,
                    mkt_price=mkt_price,
                    pnl_unrealized=fifo[3],
                    pnl_realized=fifo[2],
                    open_position=fifo[1],
                    closed_position=fifo[0])
                pnl_model.save()
                buy_lst.clear()
                sell_lst.clear()
                print('##############')

    context = {'date_form': date_form}
    return render(request, 'account/pnl.html', context)
