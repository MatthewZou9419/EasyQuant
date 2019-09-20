# -*- coding: utf-8 -*-
"""
Created on 2019/8/25 10:39
@file: plot_kline.py
@author: Matt
"""
import datetime as dt
from EasyUtil.EReportingUtil import Reporting


start_time = dt.datetime(2014, 3, 24)
end_time = dt.datetime(2019, 9, 19)
symbols_list = [
    {
        'symbol': 'RB9999.XSGE',
        'data_key': 'kline_1d',
        'query': {'time': {'$gte': start_time, '$lte': end_time}}
    }, {
        'symbol': 'HC9999.XSGE',
        'data_key': 'kline_1d',
        'query': {'time': {'$gte': start_time, '$lte': end_time}}
    },
]
Reporting().plot_kline(symbols_list)
