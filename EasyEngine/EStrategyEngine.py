# -*- coding: utf-8 -*-
"""
Created on 2019/8/7 21:16
@file: EStrategyEngine.py
@author: Matt
"""
import pandas as pd
import numpy as np
import uuid

from EasyEngine.EStrategyTarget import Order, Position, Portfolio, Context, Strategy
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
    performance = []

    def __init__(self, _strategy, _start_date, _end_date, _frequency, _portfolio_params, _reference_symbol='000001.XSHE'):
        """
        :param _strategy: 策略类
        :param _start_date: 回测开始日期
        :param _end_date: 回测结束日期
        :param _frequency: 回测频率
        :param _portfolio_params: portfolio参数
        :param _reference_symbol: 参考标的
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
        self.data_key = frequency2data_key(_frequency)
        self.strategy = _strategy
        commission_collection = self.client.get_documents('abstract', 'commission')
        commission_dict = {c['market']: c['commission'] for c in commission_collection}

        portfolio = []
        for p in _portfolio_params:
            # params check
            assert set(PORTFOLIO_PARAMS) <= set(p.keys()), \
                'Portfolio parameters should contain {}!'.format(', '.join(PORTFOLIO_PARAMS))
            starting_cash = p['_starting_cash']
            ptype = p['_ptype'] if '_ptype' in p else 'stock_cn'  # defalut ptype
            assert ptype in commission_dict, \
                'Ptype should be one of {}!'.format(', '.join(list(commission_dict.keys())))
            # starting cash check
            assert type(starting_cash) in [float, int] and starting_cash > 0, \
                'Starting cash should be a positive number!'
            commission = commission_dict[ptype]

            portfolio.append(
                Portfolio(
                    _available_cash=starting_cash,
                    _starting_cash=starting_cash,
                    _ptype=ptype,
                    _commission=commission
                )
            )
        self.context = Context(
            _portfolio=portfolio,
            _start_date=_start_date,
            _end_date=_end_date,
            _frequency=_frequency,
            _reference_symbol=_reference_symbol
        )
        market_collection = self.client.get_documents('abstract', 'market')
        self.market_dict = {m['symbol']: m['market'] for m in market_collection}

    def get_reference(self):
        market = self.market_dict[self.context.reference_symbol]
        collection_name = '{}|{}|{}'.format(self.context.reference_symbol, market, self.data_key)
        query = {'time': {'$gte': self.context.start_date, '$lte': self.context.end_date}}
        return self.client.get_documents('data', collection_name, query).sort('time')

    @staticmethod
    def make_id():
        return uuid.uuid4().hex

    def update(self, _bar):
        """
        更新函数
        :param _bar: 当前时间
        - Context.cur_bar
        - Position.price
        """
        self.context.cur_bar = _bar
        cur_time = _bar['time']
        for portfolio in self.context.portfolio:
            for symbol, position in portfolio.long_positions.items():
                position.price = self.data[symbol][cur_time]['close']
            for symbol, position in portfolio.short_positions.items():
                position.price = self.data[symbol][cur_time]['close']

        perf = {
            'time': cur_time
        }
        for i in range(len(self.context.portfolio)):
            perf['total_return{}'.format(i)] = self.context.portfolio[i].total_return,
            perf['position_pct{}'.format(i)] = \
                self.context.portfolio[i].positions_value / self.context.portfolio[i].total_value
        self.performance.append(perf)

    def get_report(self):
        # performance
        performance_df = pd.DataFrame(self.performance)
        performance_df.index = performance_df['time']
        del performance_df['time']
        benchmark = np.array([r['close'] for r in self.get_reference()])
        benchmark = benchmark / benchmark[0] - 1
        performance_df['benchmark'] = benchmark
        net_value = 1 + performance_df['total_return0']
        performance_df['drawdown'] = net_value / net_value.cummax() - 1
        # order
        orders = [{
            'add_time': o.add_time,
            'symbol': o.symbol,
            'amount': o.amount,
            'avg_cost': o.avg_cost,
            'profit': o.profit,
            'side': o.side,
            'action': o.action,
            'commission': o.commission,
            'value': o.value
        } for o in self.context.portfolio[0].orders.values()]
        order_df = pd.DataFrame(orders).sort_values('add_time')
        return performance_df, order_df

    def calc_commission(self, _value, _pindex, _action):
        """
        计算手续费
        """
        portfolio = self.context.portfolio[_pindex]
        commission = portfolio.commission
        if portfolio.ptype == 'stock_cn':
            return max(round(commission[_action] * _value, 2), commission['min'])
        return round(commission[_action] * _value, 2)

    def open(self, _symbol, _amount, _side, _pindex):
        """
        开仓函数
        """
        amount, avg_cost, commission = self.calc_open_params(_symbol, _amount, _side, _pindex)
        cur_time = self.context.cur_bar['time']
        value = amount * avg_cost
        # add a new order
        new_order = Order(
            _add_time=cur_time,
            _symbol=_symbol,
            _amount=amount,
            _avg_cost=avg_cost,  # assume instantly traded
            _profit=0,
            _side=_side,
            _action='open',
            _commission=commission
        )
        portfolio: Portfolio = self.context.portfolio[_pindex]
        portfolio.orders[self.make_id()] = new_order
        # update position
        if _side == 'long' and _symbol in portfolio.long_positions:
            position: Position = portfolio.long_positions[_symbol]
            position.avg_cost = (position.avg_cost * position.amount + value) / (position.amount + amount)
            position.amount += amount
            portfolio.available_cash -= value
        elif _side == 'short' and _symbol in portfolio.short_positions:
            pass
        # add a new position
        else:
            cur_price = self.data[_symbol][cur_time]['close']
            new_position = Position(
                _symbol=_symbol,
                _price=cur_price,
                _avg_cost=avg_cost,
                _init_time=cur_time,
                _amount=amount,
                _side=_side
            )
            if _side == 'long':
                portfolio.long_positions[_symbol] = new_position
                portfolio.available_cash -= value
            else:
                pass
        print('time: {}, symbol: {}, action: open, side: {}, amount: {}, avg_cost: {}, commission: {}'.
              format(cur_time, _symbol, _side, amount, avg_cost, commission))
        return new_order

    def close(self, _symbol, _amount, _side, _pindex):
        """
        平仓函数
        """
        amount, avg_cost, commission = self.calc_close_params(_symbol, _amount, _side, _pindex)
        cur_time = self.context.cur_bar['time']
        value = amount * avg_cost
        portfolio: Portfolio = self.context.portfolio[_pindex]
        # update position
        if _side == 'long':
            position: Position = portfolio.long_positions[_symbol]
            profit = value - position.avg_cost * amount
            # close partially
            if amount < position.amount:
                position.avg_cost = (position.avg_cost * position.amount - value) / (position.amount - amount)
                position.amount -= amount
            # close all
            else:
                portfolio.long_positions.pop(_symbol)
            # update portfolio
            portfolio.available_cash += value
        elif _side == 'short':
            pass
        # add a new order
        new_order = Order(
            _add_time=cur_time,
            _symbol=_symbol,
            _amount=amount,
            _avg_cost=avg_cost,
            _profit=profit,
            _side=_side,
            _action='close',
            _commission=commission
        )
        portfolio.orders[self.make_id()] = new_order
        print('time: {}, symbol: {}, action: close, side: {}, amount: {}, avg_cost: {}, commission: {}'.
              format(cur_time, _symbol, _side, amount, avg_cost, commission))
        return new_order

    def order_check(self, _symbol, _amount, _side, _pindex):
        """
        下单参数检查
        :param _symbol: str
        :param _amount: int or float >= 0
        :param _side: str, long or short
        :param _pindex: int, portfolio index
        """
        assert _symbol in self.market_dict, 'Symbol not found!'
        assert type(_amount) is int and _amount >= 0, \
            'Amount should be a positive number!'
        assert _side in ['long', 'short'], 'Side should be either long or short!'
        assert _pindex in range(len(self.context.portfolio)), 'Pindex out of range!'

    def calc_open_params(self, _symbol, _amount, _side, _pindex):
        """
        计算开仓参数
        """
        if _amount == 0:
            print('0 open amount!')
            return

        if _symbol not in self.data:
            market = self.market_dict[_symbol]
            collection_name = '{}|{}|{}'.format(_symbol, market, self.data_key)
            query = {'time': {'$gte': self.context.start_date, '$lte': self.context.end_date}}
            collection = self.client.get_documents('data', collection_name, query)
            self.data[_symbol] = {c['time']: c for c in collection}

        # value check
        cur_time = self.context.cur_bar['time']
        cur_price = self.data[_symbol][cur_time]['close']
        portfolio: Portfolio = self.context.portfolio[_pindex]
        unit = portfolio.commission['unit']
        margin = portfolio.commission['margin']
        _amount *= unit
        value = _amount * cur_price
        commission = self.calc_commission(value, _pindex, 'open')
        avg_cost = (value + commission) / _amount
        if value + commission > portfolio.available_cash:
            print('Not enough cash, adjusted to all cash!')
            _amount = int((portfolio.available_cash / cur_price) / unit) * unit
            if _amount == 0:
                print('0 open amount!')
                return
            value = _amount * cur_price
            commission = self.calc_commission(value, _pindex, 'open')
            avg_cost = (value + commission) / _amount

        return _amount, round(avg_cost, 2), commission

    def calc_close_params(self, _symbol, _amount, _side, _pindex):
        """
        计算平仓参数
        """
        if _amount == 0:
            print('0 close amount!')
            return

        # value check
        cur_time = self.context.cur_bar['time']
        cur_price = self.data[_symbol][cur_time]['close']
        portfolio: Portfolio = self.context.portfolio[_pindex]
        unit = portfolio.commission['unit']
        _amount *= unit
        value = _amount * cur_price
        commission = self.calc_commission(value, _pindex, 'close')
        avg_cost = (value - commission) / _amount
        position: Position = portfolio.long_positions[_symbol] if _side == 'long' else portfolio.short_positions[_symbol]
        if _amount > position.amount:
            print('Not enough amount, adjusted to all amount!')
            _amount = position.amount
            value = _amount * cur_price
            commission = self.calc_commission(value, _pindex, 'open')
            avg_cost = (value - commission) / _amount

        return _amount, round(avg_cost, 2), commission

    def order(self, _symbol, _amount, _side='long', _pindex=0):
        """
        按数量下单
        """
        self.order_check(_symbol, _amount, _side, _pindex)
        return self.open(_symbol, _amount, _side, _pindex)

    def order_target(self, _symbol, _amount, _side='long', _pindex=0):
        """
        按目标数量下单
        """
        self.order_check(_symbol, _amount, _side, _pindex)

        portfolio: Portfolio = self.context.portfolio[_pindex]
        unit = portfolio.commission['unit']
        if _side == 'long':
            if _symbol in portfolio.long_positions:
                position: Position = portfolio.long_positions[_symbol]
                if _amount > position.amount:
                    return self.open(_symbol, _amount - position.amount / unit, _side, _pindex)
                elif _amount < position.amount:
                    return self.close(_symbol, position.amount / unit - _amount, _side, _pindex)
                else:
                    print('0 close amount!')
                    return
            else:
                print('No match position!')
        else:
            pass

    def order_value(self, _symbol, _value, _side='long', _pindex=0):
        """
        按价值下单
        """

    def order_target_value(self, _symbol, _value, _side='long', _pindex=0):
        """
        按目标价值下单
        """
        
    def run(self):
        """
        策略运行
        """
        reference = self.get_reference()
        init = True
        for bar in reference:
            self.update(bar)
            
            if init:
                self.strategy.initialize(self, self.context)
                init = False
                continue    
            
            self.strategy.handle_data(self, self.context)
            
        return self.get_report()
