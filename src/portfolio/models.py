from django.db import models
from app.models import Stock, Profile


class Pnl(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL)
    date = models.DateField(null=True)
    mkt_price = models.FloatField(null=True)
    pnl_unrealized = models.FloatField(null=True)
    pnl_realized = models.FloatField(null=True)
    open_position = models.IntegerField(null=True)
    closed_position = models.IntegerField(null=True)

    def __str__(self):
        return str(self.stock)


class Fifo:
    def __init__(self, buy_list, sell_list):
        # nested lst [[quantity, mtm]]
        self.buy_lst = buy_list
        self.sell_lst = sell_list

        self.open_position = 0
        self.closed_position = 0
        self.pnl_unrealized = 0
        self.pnl_realized = 0

    def run(self):
        total_buy = sum(position[0] for position in self.buy_lst if position[0])
        total_sell = sum(position[0] for position in self.sell_lst if position[0])
        if total_sell > total_buy:
            raise ValueError('Selled more than owned')
        total_sell_pnl = sum(mtm_sell[1] for mtm_sell in self.sell_lst if mtm_sell[1])
        self.pnl_realized -= total_sell_pnl
        cumulative = 0

        for (n, x) in enumerate(self.buy_lst):
            cumulative += x[0]
            if cumulative < total_sell:
                self.pnl_realized += x[1]
                self.closed_position += x[0]
                continue
            else:
                remaining = cumulative - total_sell
                closed_pos = (self.buy_lst[n][0] - remaining)
                closed_pnl = (closed_pos / self.buy_lst[n][0]) * self.buy_lst[n][1]
                open_pnl = (remaining / self.buy_lst[n][0]) * self.buy_lst[n][1]
                self.pnl_realized += closed_pnl
                self.pnl_unrealized += open_pnl
                self.closed_position += closed_pos
                self.open_position += remaining
                for open_items in self.buy_lst[n+1:]:
                    self.pnl_unrealized += open_items[1]
                    self.open_position += open_items[0]
                return [self.closed_position, self.open_position, self.pnl_realized, self.pnl_unrealized]


