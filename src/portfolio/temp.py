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





class Fifo():
    def __init__(self):
        self.buy_queue = queue.Queue()
        self.sell_lst = queue.Queue()
        self.rest = 0
        self.pnl_unrealized = 0
        self.pnl_realized = 0
        self.open_position = 0
        self.closed_position = 0

    def run(self, lb, ls):
        for i in lb:
            self.buy_queue.put(i)
        for x in ls:
            self.sell_lst.put(x)
        while not self.buy_queue.empty():
            b_item = self.buy_queue.get()
            mtm_b, position_b = b_item[1], b_item[0]

            while not (position_b <= 0 or self.sell_lst.empty()):
                if self.rest != 0:
                    position_b -= self.rest
                    self.closed_position += self.rest
                    self.rest = 0
                s_item = self.sell_lst.get()
                mtm_s, position_s = s_item[1], s_item[0]
                position_b -= position_s
                self.closed_position += position_s
                if position_b <= 0:
                    self.rest += abs(position_b)

            if self.sell_lst.empty():
                self.open_position += position_b

        print(self.closed_position, self.open_position)


lb = [[100, 10], [100, 20]]
ls = [[50, -10], [30, -20], [22, -20]]
f = Fifo()
f.run(lb, ls)
