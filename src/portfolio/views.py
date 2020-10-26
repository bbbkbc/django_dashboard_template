from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import StockPrice, TradeHistory, Stock, Profile
from .models import Pnl
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

            buy_trades = []
            sell_trades = []
            for trade in trade_history:
                if trade.site == 'K':
                    buy_trades.append(trade)
                else:
                    sell_trades.append(trade)

            # unrealized pnl
            if len(sell_trades) == 0:
                if Pnl.objects.filter(stock=stock_name).exists():
                    print('pnl for', stock_name, 'exist')

                else:
                    pnl_lst = []
                    for item_buy in buy_trades:
                        item_date = item_buy.date_time.date()
                        days_number = int((end_date - item_date).days)
                        for n in range(days_number):
                            evaluation_day = item_date + timedelta(n)
                            price_history = StockPrice.objects.all().filter(stock=stock_name).filter(date=evaluation_day)
                            try:
                                close_price = price_history[0].close
                                pnl_unrealized = (close_price - item_buy.stock_price) * item_buy.num_of_share
                                position_value_at_now = item_buy.num_of_share * close_price
                                position_value_at_open = item_buy.num_of_share * item_buy.stock_price
                                num_of_share_live = int(item_buy.num_of_share)

                                pnl_lst.append([
                                    evaluation_day,
                                    round(pnl_unrealized, ndigits=2),
                                    close_price,
                                    position_value_at_open,
                                    position_value_at_now,
                                    num_of_share_live])

                            except IndexError:
                                continue

                    df = pd.DataFrame(pnl_lst[:], columns=[
                        'date',
                        'pnl_u',
                        'mkt_price',
                        'position_value_at_open',
                        'position_value_at_now',
                        'num_of_share_live'])
                    df = df.groupby(df['date']).sum()

                    for i in df.itertuples():
                        pnl_unrealized = Pnl(
                            user=user_id,
                            stock=stock_name,
                            pnl_live=i.pnl_u,
                            pnl_booked=0,
                            mkt_price=i.mkt_price,
                            position_value_at_open=i.position_value_at_open,
                            position_value_at_now=i.position_value_at_now,
                            num_of_share_live=i.num_of_share_live,
                            num_of_share_realized=0,
                            date=i.Index)
                        pnl_unrealized.save()

            elif len(sell_trades) != 0:
                trade_lst = []
                # unpack queries
                for buy_trade in buy_trades:
                    trade_lst.append(
                        [buy_trade.date_time.date(),
                         buy_trade.stock_price,
                         buy_trade.num_of_share,
                         'buy'])
                for sell_trade in sell_trades:
                    trade_lst.append(
                        [sell_trade.date_time.date(),
                         sell_trade.stock_price,
                         sell_trade.num_of_share,
                         'sell'])
                deals = pd.DataFrame(data=trade_lst[:], columns=['date', 'price', 'quantity', 'side'])
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

                dmtm = deals_mtm.groupby(deals_mtm['date']).get_group()

    context = {'date_form': date_form}
    return render(request, 'account/pnl.html', context)
