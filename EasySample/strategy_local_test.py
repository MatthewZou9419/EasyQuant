# -*- coding: utf-8 -*-
"""
Created on 2019/8/8 上午11:51 
@file: strategy_local_test.py
@author: ZouHao
"""
from collections import deque
import numpy as np

from EasyEngine.EStrategyEngine import Engine
from EasyEngine.EStrategyTarget import Strategy
from EasyUtil.EReportingUtil import plot_performance, get_statistics


# --------------------------策略撰写--------------------------
class TestStrategy(Strategy):
    def initialize(self, context):
        self.atr_window = 14
        self.atr_n = 1
        self.add_pct = 0.1
        self.stop_win_pct = 0.1
        self.stop_loss_pct = 0.1
        self.tr_q = deque(maxlen=self.atr_window)
        self.close_q = deque(maxlen=2)
        self.open_q = deque(maxlen=2)
        self.code = '000001.XSHE'

    def handle_data(self, context):
        high = context.cur_bar['high']
        low = context.cur_bar['low']
        close = context.cur_bar['close']
        self.close_q.append(close)
        if len(self.close_q) < 2:
            return 
        tr = max([high - low, abs(high - self.close_q[0]), abs(self.close_q[0] - low)])
        self.tr_q.append(tr)
        if len(self.tr_q) < self.atr_window:
            return 
        atr = np.mean(self.tr_q)
        # first open
        if context.portfolio[0].positions_value == 0 and close - self.close_q[0] > self.atr_n * atr:
            cash = context.portfolio[0].available_cash * self.add_pct
            amount = int((cash / close) / 100)
            order = e.order(self.code, amount)
            self.open_q.append(order.avg_cost)
        # add position
        elif close > np.mean(self.open_q) * (1 + self.stop_win_pct):
            cash = context.portfolio[0].available_cash * self.add_pct
            amount = int((cash / close) / 100)
            order = e.order(self.code, amount)
            self.open_q.append(order.avg_cost)
        # close
        elif close < np.mean(self.open_q) * (1 - self.stop_loss_pct):
            e.order_target(self.code, 0)
            self.open_q.clear()


# --------------------------策略运行--------------------------
start_date = '2005-1-1'
end_date = '2019-8-20'
frequency = 'day'
portfolio_params = {
    '_starting_cash': 1000000,
}
reference_symbol = '000001.XSHE'

e = Engine(
    _strategy=TestStrategy,
    _start_date=start_date,
    _end_date=end_date,
    _frequency=frequency,
    _portfolio_params=portfolio_params,
    _reference_symbol=reference_symbol
)

performance_df, order_df = e.run()
stats = get_statistics(performance_df, order_df)
plot_performance(performance_df)
for k, v in stats.items():
    print('{}: {}'.format(k, v))
