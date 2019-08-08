# -*- coding: utf-8 -*-
"""
Created on 2019/8/8 上午11:51 
@file: EStrategyLocalTest.py
@author: ZouHao
"""
from EasyEngine import EStrategyEngine

universe = '000001.XSHE'
start_date = '2019-1-1'
end_date = '2019-1-5'
frequency = 'day'
portfolio_params = {'_starting_cash': 1000000, '_ptype': 'stock_cn'}

engine = EStrategyEngine.Engine(
    _universe=universe,
    _start_date=start_date,
    _end_date=end_date,
    _frequency=frequency,
    _portfolio_params=portfolio_params
)
