#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- check_stocks.py ---

Checks stocks module.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


from stocks import Stock, StockFactory


def check_stock_init():
    print(f'--- check_stock_init() ---')
    stock = Stock('AAPL', period='max', interval='1mo')
    print(stock.history)


def check_stock_init_with_rsi():
    print(f'--- check_stock_init_w_rsi() ---')
    stock = Stock('AAPL', indicators='RSI', window=60)
    stock.refresh()
    print(stock.history)


def check_stock_factory():
    print(f'--- check_stock_factory() ---')
    symbols = ['AAPL', 'MSFT', 'AI', 'PLTR', 'CCL', 'U', 'V', 'V']
    stocks = StockFactory.create(symbols, indicators='RSI', window=60)
    for stock in stocks:
        print(f'--- {stock.symbol}---\n{stock.history}\n')


if __name__ == '__main__':
    check_stock_init()
    check_stock_init_with_rsi()
    check_stock_factory()
