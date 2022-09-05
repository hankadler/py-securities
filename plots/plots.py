#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- plots.py ---

Contains Plotter class definition.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


import matplotlib.pyplot as plt

from stocks import Stock


class Plotter:
    @staticmethod
    def plot(stock: Stock):
        fig, axs = plt.subplots(3, 1)
        fig.suptitle(stock.symbol, size=24, weight='bold')

        h = stock.history

        price_ax = h['Low'].plot.kde(ax=axs[0])
        price_ax.set_xlim(left=h['Low'].min(), right=h['Low'].max())
        price_ax.set_ylabel('Price')
        price_ax.axvline(x=h['Low'][-1], lw=0.5, color='black')
        y_mid = sum(price_ax.get_ylim()) / len(price_ax.get_ylim())
        price_ax.text(
            h['Low'][-1] * 1.005, y_mid, f'{h["Low"][-1]}', rotation=90)

        rsi_ax = h['RSI'].plot.kde(ax=axs[1])
        rsi_ax.set_xlim(left=h['RSI'].min(), right=h['RSI'].max())
        rsi_ax.set_ylabel('RSI')
        rsi_ax.axvline(x=h['RSI'][-1], lw=0.5, color='black')
        y_mid = sum(rsi_ax.get_ylim()) / len(rsi_ax.get_ylim())
        rsi_ax.text(
            h['RSI'][-1] * 1.005, y_mid, f'{h["RSI"][-1]}', rotation=90)

        open_vols = h.groupby(h.index.date)['Volume'].first()
        norm_open_vols = (open_vols / open_vols.max()).round(2)
        vol_ax = norm_open_vols.plot.kde(ax=axs[2])
        vol_ax.set_xlim(left=0, right=1)
        vol_ax.set_ylabel('Norm. Open Vol')
        vol_ax.axvline(x=norm_open_vols[-1], lw=0.5, color='black')
        y_mid = sum(vol_ax.get_ylim()) / len(vol_ax.get_ylim())
        vol_ax.text(
            norm_open_vols[-1] * 1.005, y_mid, f'{norm_open_vols[-1]}',
            rotation=90)

        plt.get_current_fig_manager().window.showMaximized()
        plt.show()


if __name__ == '__main__':
    stock = Stock('PLTR', indicators='RSI')
    Plotter.plot(stock)
