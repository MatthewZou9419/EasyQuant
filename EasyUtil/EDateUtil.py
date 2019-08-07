# -*- coding: utf-8 -*-
"""
Created on 2019/8/7 22:54
@file: EDateUtil.py
@author: Matt
"""
import datetime as dt


def str2date(_date):
    return dt.datetime.strptime(_date, '%Y-%m-%d')
