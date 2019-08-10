# -*- coding: utf-8 -*-
"""
Created on 2019/8/10 12:06
@file: EConvertUtil.py
@author: Matt
"""


def frequency2data_key(_frequency):
    if _frequency == 'day':
        return 'kline_1d'
    elif _frequency == 'minute':
        return 'kline_1m'
    elif _frequency == 'tick':
        return 'tick'
