# -*- coding: utf-8 -*-
"""
Created on 2019/8/21 下午4:16 
@file: EReportingUtil.py
@author: ZouHao
"""
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def plot_performance(performance_df):
    plt.figure(figsize=(12, 6))
    plt.subplot(211)
    plt.ylim([-1, 0])
    plt.fill_between(performance_df.index, performance_df['drawdown'], 0, label='drawdown', color='gray', alpha=0.5)
    plt.twinx()
    plt.plot(performance_df['total_return'], label='total_return')
    plt.plot(performance_df['benchmark'], label='benchmark')
    plt.axhline(0, c='k')
    plt.legend()
    plt.subplot(212)
    plt.ylim([0, 1])
    plt.fill_between(performance_df.index, performance_df['position_pct0'], 0, label='position_pct0', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig('../EasyGraph/performance.png')


def get_statistics(performance_df, order_df):
    # total return
    total_return = performance_df['total_return'][-1]
    bench_total_return = performance_df['benchmark'][-1]
    # annual return
    annual_return = (1 + total_return) ** (250 / len(performance_df)) - 1
    bench_annual_return = (1 + bench_total_return) ** (250 / len(performance_df)) - 1
    net_value = 1 + performance_df['total_return']
    bench_net_value = 1 + performance_df['benchmark']
    daily_return = (net_value / net_value.shift() - 1).dropna()
    bench_daily_return = (bench_net_value / bench_net_value.shift() - 1).dropna()
    # alpha & beta
    beta = np.cov(daily_return, bench_daily_return)[0, 1] / np.var(bench_daily_return)
    rf = 0.04
    alpha = annual_return - (beta * (bench_annual_return - rf) + rf)
    # vol & sharpe
    vol = np.std(daily_return) * np.sqrt(250)
    bench_vol = np.std(bench_daily_return) * np.sqrt(250)
    sharpe = (annual_return - rf) / vol
    # win/loss
    profit = order_df['profit']
    win_loss = profit[profit > 0].sum() / abs(profit[profit < 0].sum())
    # max drawdown
    max_dd = performance_df['drawdown'].min()
    # win pct
    win_pct = (profit > 0).sum() / (profit != 0).sum()

    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'alpha': alpha,
        'beta': beta,
        'sharpe': sharpe,
        'vol': vol,
        'max_drawdown': max_dd,
        'win_pct': win_pct,
        'win/loss': win_loss
    }
