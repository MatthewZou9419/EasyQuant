# -*- coding: utf-8 -*-
"""
Created on 2019/8/7 21:16
@file: EStrategyEngine.py
@author: Matt
"""
import uuid

from EasyUtil.EConstantsUtil import FREQUENCY, COMMISSION, DATA
from EasyUtil.EDateUtil import str2date
from EasyUtil.EMongoUtil import MongoClient


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
                 _starting_cash, _positions_value, _type):
        self.available_cash = _available_cash  # 可用资金
        self.long_positions = _long_positions  # 多仓
        self.short_positions = _short_positions  # 空仓
        self.orders = _orders  # 所有订单
        self.total_value = _total_value  # 总价值
        self.total_return = _total_return  # 收益率
        self.starting_cash = _starting_cash  # 初始资金
        self.positions_value = _positions_value  # 仓位价值
        self.type = _type  # 账户类型


class Context:
    """
    策略信息类
    """

    def __init__(self, _portfolio, _cur_time, _universe, _start_date, _end_date, _frequency):
        self.portfolio = _portfolio  # 资产组合
        self.cur_time = _cur_time  # 当前时间
        self.universe = _universe  # 标的池
        self.start_date = _start_date  # 策略开始日期
        self.end_date = _end_date  # 策略结束日期
        self.frequency = _frequency  # 运行频率


class Engine:
    """
    交易引擎类
    """

    def __init__(self, _starting_cash, _universe, _start_date, _end_date, _frequency, _type):
        # starting cash check
        assert type(_starting_cash) in [float, int] and _starting_cash > 0, \
            'Starting cash should be a positive number!'
        # date type check
        try:
            _start_date = str2date(_start_date)
            _end_date = str2date(_end_date)
        except ValueError:
            raise Exception('Date type should be like Year-Month-Day!')
        # frequency check
        assert _frequency in FREQUENCY, \
            'Frequency should be one of {}!'.format(', '.join(FREQUENCY))
        # type check
        markets = [c['market'] for c in COMMISSION]
        assert _type in markets

        self.commission = COMMISSION[markets.index(_type)]['commission']
        self.context = Context(
            _portfolio=Portfolio(
                _available_cash=_starting_cash,
                _long_positions={},
                _short_positions={},
                _orders={},
                _total_value=_starting_cash,
                _total_return=0,
                _starting_cash=_starting_cash,
                _positions_value=0,
                _type=_type
            ),
            _cur_time=None,
            _universe=_universe,
            _start_date=_start_date,
            _end_date=_end_date,
            _frequency=_frequency
        )
        self.client = MongoClient()

    @staticmethod
    def make_id():
        return uuid.uuid4().hex

    def update(self):
        pass

    def calc_commission(self):
        """
        计算手续费
        """
        pass

    @staticmethod
    def order_check(_symbol, _amount, _value, _side):
        """
        下单函数参数检查
        :param _symbol: str
        :param _amount: int or float >= 0
        :param _value: int or float >= 0
        :param _side: str, long or short
        """
        assert isinstance(_symbol, str), 'Symbol should be a string!'
        if _amount is not None:
            assert type(_amount) in [float, int] and _amount >= 0, \
                'Amount should be a positive number!'
        if _value is not None:
            assert type(_value) in [float, int] and _value >= 0, \
                'Value should be a positive number!'
        assert _side in ['long', 'short'], 'Side should be either long or short!'

    def order(self, _symbol, _amount, _side='long'):
        """
        按数量下单
        """
        self.order_check(_symbol=_symbol, _amount=_amount, _value=None, _side=_side)

        cur_time = self.context.cur_time
        '''get price from db'''
        cur_price = 10
        '''calc commission from class method'''
        commission = 5
        new_order = Order(
            _add_time=cur_time,
            _symbol=_symbol,
            _amount=_amount,
            _avg_cost=cur_price,
            _side=_side,
            _action='open',
            _commission=commission
        )
        self.context.portfolio.orders[self.make_id()] = new_order

        if _side == 'long' and _symbol in self.context.portfolio.long_positions:
            pass
        elif _side == 'short' and _symbol in self.context.portfolio.short_positions:
            pass
        else:
            new_position = Position(
                _symbol=_symbol,
                _price=cur_price,
                _avg_cost=cur_price,
                _init_time=cur_time,
                _amount=_amount,
                _value=cur_price * _amount,
                _side=_side
            )
            if _side == 'long':
                self.context.portfolio.long_positions[_symbol] = new_position
            else:
                self.context.portfolio.short_positions[_symbol] = new_position

    def order_target(self, _symbol, _amount, _side='long'):
        """
        按目标数量下单
        """
        self.order_check(_symbol=_symbol, _amount=_amount, _value=None, _side=_side)

    def order_value(self, _symbol, _value, _side='long'):
        """
        按价值下单
        """
        self.order_check(_symbol=_symbol, _amount=None, _value=_value, _side=_side)

    def order_target_value(self, _symbol, _value, _side='long'):
        """
        按目标价值下单
        """
        self.order_check(_symbol=_symbol, _amount=None, _value=_value, _side=_side)
