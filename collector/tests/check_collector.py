#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- check_collector.py ---

Checks collector module.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


from collector import Collector


def check_parm_validation():
    symbol = 'AAPL'
    try:
        history = Collector.get_history(symbol, period='foo')
    except:
        print('`period` validation works!')
        pass
    try:
        history = Collector.get_history(symbol, interval='foo')
    except:
        print('`interval` validation works!')
        pass
    print()


def check_get_history_yf():
    symbol = 'AAPL'
    history = Collector.get_history(symbol)
    print(f'--- {symbol} ---\n{history}\n')
    print(history['Low'])

    # symbol = 'AI'
    # history = Collector.get_history(symbol)
    # print(f'--- {symbol} ---\n{history}\n')


if __name__ == '__main__':
    check_parm_validation()
    check_get_history_yf()
