# -*- coding: utf-8 -*-
"""
Created on 2019/8/8 上午11:51 
@file: EStrategyLocalTest.py
@author: ZouHao
"""
from tqdm import tqdm

from EasyEngine import EStrategyEngine
from EasyUtil.EMongoUtil import MongoClient

client = MongoClient()

# --------------------------初始化参数设定--------------------------
start_date = '2019-1-1'
end_date = '2019-8-5'
frequency = 'day'
portfolio_params = {
    '_starting_cash': 1000000,
}
reference_symbol = '000001.XSHE'

engine = EStrategyEngine.Engine(
    _start_date=start_date,
    _end_date=end_date,
    _frequency=frequency,
    _portfolio_params=portfolio_params,
    _reference_symbol=reference_symbol
)

reference = engine.get_reference()

# --------------------------策略撰写--------------------------
for bar in tqdm(reference):
    pass
