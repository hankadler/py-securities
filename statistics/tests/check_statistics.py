#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- check_statistics.py ---

Checks statistics module.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""

import config, utils
from stocks import Stock, StockFactory
from statistics import Statistic

screened_txt = f'{config.ASSETS_DIR}/stocks-screened.txt'
symbols = utils.txt2symbols(screened_txt)
print('Initializing stocks...')
stocks = StockFactory.create(symbols, indicators='RSI', window=60)
stocks = [s for s in stocks if s is not None]
out_dir = './output'


def check_firstn():
    stock = Stock('PLTR', indicators='RSI', window=60)
    stat = Statistic(stock, what='FirstN', x=9)
    print(stat)


def check_volrsi():
    stock = Stock('PLTR', indicators='RSI', window=60)
    stat = Statistic(stock, what='VolRSI')
    print(stat)


def check_simplersi():
    # stock = Stock('PLTR', indicators_remaining='RSI', window=60)
    for stock in stocks:
        stat = Statistic(stock, what='SimpleRSI')
        print(stat)


def check_gobo():
    # stock = Stock('PLTR')
    for stock in stocks:
        stat = Statistic(stock, what='Gobo')
        print(stat)


def check_hourlychg():
    for stock in stocks:
        stat = Statistic(stock, what='HourlyChg')
        print(stat)

        path = f'{out_dir}/{stock.symbol}-HourlyChg.txt'
        with open(path, 'w') as f:
            f.write(str(stat))
        print(f"HourlyChg statistics written to '{path}'.")


if __name__ == '__main__':
    # check_firstn()
    # check_volrsi()
    # check_simplersi()
    #check_gobo()
    check_hourlychg()
