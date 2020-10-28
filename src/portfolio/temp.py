import queue
import numpy as np

l1 = [10, 10, 10, 10]
l2 = [5, 2, 19]

# def fifo(l1, l2):
#     total_selled = sum(l2)
#     if total_selled > sum(l1):
#         raise ValueError('Selled more than owned')
#     cumulative = 0
#     ret = []
#
#     for (n, x) in enumerate(l1):
#         cumulative += x
#         if cumulative < total_selled:
#             ret.append(0)
#             continue
#         else:
#             remaining = cumulative - total_selled
#             ret.append(remaining)
#             return_value = ret + l1[n + 1:]
#             return return_value

# pnl_live = models.FloatField()
# pnl_booked = models.FloatField()
# mkt_price = models.FloatField()
# position_value_at_open = models.FloatField()
# position_value_at_now = models.FloatField()
#
# date = models.DateField()


class Fifo:
    def __init__(self, buy_list, sell_list):
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
        ret = []

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
                print()
                for open_items in self.buy_lst[n+1:]:
                    self.pnl_unrealized += open_items[1]
                    self.open_position += open_items[0]
                return [self.closed_position, self.open_position, self.pnl_realized, self.pnl_unrealized]


lb = [[100, 10], [100, 20], [50, 50], [20, 10], [30, 20]]
ls = [[50, -10], [150, -10], [10, -10]]
f = Fifo(buy_list=lb, sell_list=ls)
print(f.run())



