# -*- coding: utf-8 -*-
"""
Created on 2019/8/8 上午11:51 
@file: EStrategyLocalTest.py
@author: ZouHao
"""
from collections import deque
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm

from EasyEngine.EStrategyEngine import Engine
from EasyUtil.EMongoUtil import MongoClient

client = MongoClient()

# --------------------------初始化参数设定--------------------------
start_date = '2019-1-1'
end_date = '2019-8-20'
frequency = 'day'
portfolio_params = {
    '_starting_cash': 1000000,
}
reference_symbol = '000001.XSHE'

e = Engine(
    _start_date=start_date,
    _end_date=end_date,
    _frequency=frequency,
    _portfolio_params=portfolio_params,
    _reference_symbol=reference_symbol
)

reference = e.get_reference()

# --------------------------策略撰写--------------------------
w1 = 5
w2 = 10
q = deque(maxlen=w2)
code = '000001.XSHE'
for bar in reference:
    e.update(bar['time'])

    q.append(bar['close'])
    if len(q) < w2:
        continue
    if e.context.portfolio[0].positions_value == 0 and np.mean(list(q)[-w1:]) > np.mean(q):
        e.order(code, 10000)
    elif e.context.portfolio[0].positions_value > 0 and np.mean(list(q)[-w1:]) < np.mean(q):
        e.order_target(code, 0)

performance_df = pd.DataFrame(e.performance)
performance_df.index = performance_df['time']
del performance_df['time']
performance_df.plot(secondary_y='position_pct')
plt.show()
