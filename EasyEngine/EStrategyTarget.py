# -*- coding: utf-8 -*-
"""
Created on 2019/8/10 13:13
@file: EStrategyTarget.py
@author: Matt
"""


class Order:
    """
    订单类
    """

    def __init__(self, _add_time, _symbol, _amount, _avg_cost, _side, _action, _commission):
        self.add_time = _add_time  # 时间
        self.symbol = _symbol  # 标的
        self.amount = _amount  # 数量
        self.avg_cost = _avg_cost  # 平均成本
        self.side = _side  # 多空方向
        self.action = _action  # 开平方向
        self.commission = _commission  # 手续费


class Position:
    """
    持仓标的类
    """

    def __init__(self, _symbol, _price, _avg_cost, _init_time, _amount, _value, _side):
        self.symbol = _symbol  # 标的
        self.price = _price  # 最新价
        self.avg_cost = _avg_cost  # 平均成本
        self.init_time = _init_time  # 建仓时间
        self.amount = _amount  # 数量
        self.value = _value  # 价值
        self.side = _side  # 多空方向


class Portfolio:
    """
    账户类
    """

    def __init__(self, _available_cash, _long_positions, _short_positions, _orders, _total_value, _total_return,
                 _starting_cash, _positions_value, _ptype, _commission):
        self.available_cash = _available_cash  # 可用资金
        self.long_positions = _long_positions  # 多仓
        self.short_positions = _short_positions  # 空仓
        self.orders = _orders  # 所有订单
        self.total_value = _total_value  # 总价值
        self.total_return = _total_return  # 收益率
        self.starting_cash = _starting_cash  # 初始资金
        self.positions_value = _positions_value  # 仓位价值
        self.ptype = _ptype  # 账户类型
        self.commission = _commission  # 手续费


class Context:
    """
    策略信息类
    """

    def __init__(self, _portfolio, _cur_time, _start_date, _end_date, _frequency, _reference_symbol):
        self.portfolio = _portfolio  # 资产组合
        self.cur_time = _cur_time  # 当前时间
        self.start_date = _start_date  # 策略开始日期
        self.end_date = _end_date  # 策略结束日期
        self.frequency = _frequency  # 运行频率
        self.reference_symbol = _reference_symbol  # 参考标的
