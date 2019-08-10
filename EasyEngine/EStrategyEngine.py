# -*- coding: utf-8 -*-
"""
Created on 2019/8/7 21:16
@file: EStrategyEngine.py
@author: Matt
"""
import uuid

from EasyEngine.EStrategyTarget import Order, Position, Portfolio, Context
from EasyUtil.EConstantsUtil import FREQUENCY, PORTFOLIO_PARAMS
from EasyUtil.EConvertUtil import frequency2data_key
from EasyUtil.EDateUtil import str2date
from EasyUtil.EMongoUtil import MongoClient


class Engine:
    """
    交易引擎类
    """
    client = MongoClient()
    data = {}

    def __init__(self, _start_date, _end_date, _frequency, _portfolio_params):
        """
        :param _start_date: 回测开始日期
        :param _end_date: 回测结束日期
        :param _frequency: 回测频率
        :param _portfolio_params: portfolio参数
        """
        if not isinstance(_portfolio_params, list):
            _portfolio_params = [_portfolio_params]
        # date type check
        try:
            _start_date = str2date(_start_date)
            _end_date = str2date(_end_date)
        except ValueError:
            raise Exception('Date type should be like Year-Month-Day!')
        # frequency check
        assert _frequency in FREQUENCY, 'Frequency should be one of {}!'.format(', '.join(FREQUENCY))
        commission_collection = self.client.get_documents('abstract', 'commission')
        commission_dict = {c['market']: c['commission'] for c in commission_collection}

        self.data_key = frequency2data_key(_frequency)
        portfolio = []
        for p in _portfolio_params:
            # params check
            assert set(PORTFOLIO_PARAMS) <= set(p.keys()), \
                'Portfolio parameters should contain {}!'.format(', '.join(PORTFOLIO_PARAMS))
            starting_cash = p['_starting_cash']
            ptype = p['_ptype'] if '_ptype' in p else 'stock_cn'  # defalut ptype is stock_cn
            assert ptype in commission_dict, \
                'Ptype should be one of {}!'.format(', '.join(list(commission_dict.keys())))
            # starting cash check
            assert type(starting_cash) in [float, int] and starting_cash > 0, \
                'Starting cash should be a positive number!'
            commission = commission_dict[ptype]

            portfolio.append(
                Portfolio(
                    _available_cash=starting_cash,
                    _long_positions={},
                    _short_positions={},
                    _orders={},
                    _total_value=starting_cash,
                    _total_return=0,
                    _starting_cash=starting_cash,
                    _positions_value=0,
                    _ptype=ptype,
                    _commission=commission
                )
            )
        self.context = Context(
            _portfolio=portfolio,
            _cur_time=None,
            _start_date=_start_date,
            _end_date=_end_date,
            _frequency=_frequency
        )
        market_collection = self.client.get_documents('abstract', 'market')
        self.market_dict = {m['symbol']: m['market'] for m in market_collection}

    @staticmethod
    def make_id():
        return uuid.uuid4().hex

    def update(self, _time):
        """
        更新函数
        :param _time: 当前时间
        - Context.cur_time
        - Position.price
        - Position.value
        - Portfolio.total_value
        - Portfolio.total_return
        - Portfolio.positions_value
        """
        self.context.cur_time = _time
        for portfolio in self.context.portfolio:
            positions_value = 0
            for symbol, position in portfolio.long_positions.items():
                position.price = self.data[symbol][_time]['close']
                position.value = position.amount * position.price
                positions_value += position.value
            for position in portfolio.short_positions:
                pass
            portfolio.total_value = positions_value + portfolio.available_cash
            portfolio.total_return = portfolio.total_value / portfolio.starting_cash - 1
            portfolio.positions_value = positions_value

    def calc_commission(self):
        """
        计算手续费
        """
        pass

    def order_check(self, _symbol, _amount, _value, _side, _pindex):
        """
        下单函数参数检查
        :param _symbol: str
        :param _amount: int or float >= 0
        :param _value: int or float >= 0
        :param _side: str, long or short
        :param _pindex: int, portfolio index
        """
        if _amount is None and _value is None:
            raise Exception('Amount and value cannot be None at the same time!')
        if _amount is not None:
            assert type(_amount) in [float, int] and _amount >= 0, \
                'Amount should be a positive number!'
        if _value is not None:
            assert type(_value) in [float, int] and _value >= 0, \
                'Value should be a positive number!'
        assert _side in ['long', 'short'], 'Side should be either long or short!'
        assert _pindex in range(len(self.context.portfolio)), 'Pindex out of range!'

    def order(self, _symbol, _amount, _side='long', _pindex=0):
        """
        按数量下单
        """
        self.order_check(_symbol=_symbol, _amount=_amount, _value=None, _side=_side, _pindex=_pindex)

        if _symbol not in self.data:
            market = self.market_dict[_symbol]
            collection_name = '{}|{}|{}'.format(_symbol, market, self.data_key)
            collection = self.client.get_documents('data', collection_name)
            self.data[_symbol] = {c['time']: c for c in collection}

        # add a new order
        cur_time = self.context.cur_time
        cur_price = self.data[_symbol][cur_time]['close']
        new_order = Order(
            _add_time=cur_time,
            _symbol=_symbol,
            _amount=_amount,
            _avg_cost=cur_price,
            _side=_side,
            _action='open',
            _commission=self.context.portfolio[_pindex].commission['open']
        )
        self.context.portfolio[_pindex].orders[self.make_id()] = new_order

        # update position
        if _side == 'long' and _symbol in self.context.portfolio[_pindex].long_positions:
            position: Position = self.context.portfolio[_pindex].long_positions[_symbol]
            acc_amount = _amount + position.amount
            acc_value = _amount * cur_price + position.value
            avg_cost = acc_value / acc_amount
            # update position
            position.avg_cost = avg_cost
            position.amount = acc_amount
            position.value = acc_value
        elif _side == 'short' and _symbol in self.context.portfolio[_pindex].short_positions:
            pass
        else:
            new_position = Position(
                _symbol=_symbol,
                _price=cur_price,
                _avg_cost=cur_price,
                _init_time=cur_time,
                _amount=_amount,
                _value=_amount * cur_price,
                _side=_side
            )
            if _side == 'long':
                self.context.portfolio[_pindex].long_positions[_symbol] = new_position
            else:
                self.context.portfolio[_pindex].short_positions[_symbol] = new_position

        # update portfolio
        self.context.portfolio[_pindex].available_cash -= (_amount * cur_price)
        self.context.portfolio[_pindex].positions_value += (_amount * cur_price)

    def order_target(self, _symbol, _amount, _side='long', _pindex=0):
        """
        按目标数量下单
        """

    def order_value(self, _symbol, _value, _side='long', _pindex=0):
        """
        按价值下单
        """

    def order_target_value(self, _symbol, _value, _side='long', _pindex=0):
        """
        按目标价值下单
        """

    def run(self):
        trade_calendar = self.client.get_documents(
            'abstract',
            'trade_calendar',
            {'date': {'$gte': self.context.start_date}}
        )
        a = 0
        for row in trade_calendar:
            t = row['date']
            self.update(t)

            if a == 0:
                self.order('000001.XSHE', 100)
                a = 1
