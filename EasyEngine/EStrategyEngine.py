# -*- coding: utf-8 -*-
"""
Created on 2019/8/7 21:16
@file: EStrategyEngine.py
@author: Matt
"""


class Order:
    """
    订单类
    """
    def __init__(self, _add_time, _symbol, _amount, _avg_cost, _side, _action, _commission):
        self.add_time = _add_time      # 时间
        self.symbol = _symbol          # 标的
        self.amount = _amount          # 数量
        self.avg_cost = _avg_cost      # 平均成本
        self.side = _side              # 多空方向
        self.action = _action          # 开平方向
        self.commission = _commission  # 手续费

    def order(self, _symbol, _amount, _side='long'):
        """

        :return:
        """
