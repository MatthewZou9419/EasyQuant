# -*- coding: utf-8 -*-
"""
Created on 2019/8/8 上午9:58 
@file: EConstantsUtil.py
@author: ZouHao
"""
import datetime as dt

FREQUENCY = ['day', 'minute', 'tick']
COMMISSION = [
    {
        'market': 'stock_cn',
        'commission': {'open': 0.00025, 'close': 0.001, 'unit': 100}
    }
]
DATA = [
    {
        'time': dt.datetime(2019, 1, 1),
        'close': 9.5
    }, {
        'time': dt.datetime(2019, 1, 2),
        'close': 1.2
    }, {
        'time': dt.datetime(2019, 1, 3),
        'close': 1.72
    }, {
        'time': dt.datetime(2019, 1, 4),
        'close': 6.54
    }, {
        'time': dt.datetime(2019, 1, 5),
        'close': 8.23
    }
]
