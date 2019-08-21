# -*- coding: utf-8 -*-
"""
Created on 2019/8/21 下午4:16 
@file: EReportingUtil.py
@author: ZouHao
"""
import matplotlib.pyplot as plt


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
    plt.show()
