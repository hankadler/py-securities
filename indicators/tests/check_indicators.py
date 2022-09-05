#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- check_indicators.py ---

Checks indicators_remaining module.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


from collector import Collector
from indicators import Indicators


def main():
    history = Collector.get_history('AAPL')
    rsi = Indicators.RSI(history['Low'], 60)
    print(rsi)


if __name__ == '__main__':
    main()
