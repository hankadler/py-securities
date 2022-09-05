#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- stocks.py ---

An equity security that represents fractional ownership of a company.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


import pandas as pd

import args2fields as a2f
from collector import Collector
from indicators import Indicators


class Stock:
    def __init__(
            self, symbol: str, period='60d',
            interval=Collector.DEFAULT_INTERVALS['60d'],
            start: str = None, end: str = None, source=Collector.SOURCES[0],
            indicators=[], **kwargs):
        """
        Parameters:
            symbol (str): Stock symbol.
            period (str): Period to latest quote. See `Collector.MAX_PERIODS`.
            interval (str): Data intervals. See `Collector.VALID_INTERVALS`.
            start (str): Date indicating period start.
            end (str): Date indicating period end.
            source (str): Data source. See `Collector.SOURCES`.
            indicators (list): Names of indicators_remaining to add to `history`.
        """
        self._kwargs = kwargs
        self._history = None

        self.symbol = symbol
        self.period = period
        self.interval = interval
        self.start = start
        self.end = end
        self.source = source
        if isinstance(indicators, str):
            indicators = indicators.split()
        self.indicators = indicators

        self.refresh()

    """history (df): index=Datetime, columns=Open|High|Low|Close|Volume"""
    @property
    def history(self):
        return self._history
    @history.setter
    def history(self, value):
        if isinstance(value, pd.DataFrame):
            self._history = value
            self._on_set_history()
        else:
            self._history = None

    # @Helper
    def _on_set_history(self):
        for indicator in self.indicators:
            if indicator.upper() == 'RSI':
                # Parses `kwargs` for any required field.
                fields = {'window': int}
                defaults = {'window': 60}
                a2f.args2fields(self, fields, defaults=defaults, **self._kwargs)

                # Adds RSI column to `history`.
                rsi = Indicators.RSI(self.history['Low'], self.window)
                self._history['RSI'] = rsi

    def refresh(self):
        self.history = Collector.get_history(
            self.symbol, self.period, self.interval, self.start, self.end,
            self.source)


class StockFactory:
    @classmethod
    def create(cls, symbols: any, **kwargs):
        """Returns a list of Stock instances created from `symbols`.

        Parameters:
            symbols (any -> list): Stocks symbols.
        """
        if isinstance(symbols, str):
            symbols = symbols.split()
        if len(symbols) > 1:
            symbols = sorted(set(symbols))
        return [Stock(symbol, **kwargs) for symbol in symbols]


if __name__ == '__main__':
    pass
