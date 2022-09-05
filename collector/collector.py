#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- collector.py ---

Collects stock data from `source`.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


import datetime as dt
import re

import yfinance as yf


class Collector:
    """A library class that collects stock data.

    Attributes:
        SOURCES (list): Sources from which stock data can be pulled.
        MAX_PERIODS (list): Max periods allowed.
        VALID_INTERVALS (list): Valid intervals.
        DEFAULT_INTERVALS (dict): Default intervals per period.
    """
    SOURCES = ['yfinance', 'iex']
    MAX_PERIODS = ['730d', '104wk', '23mo', 'ytd', 'max']
    VALID_PERIODS = ['1d', '7d', '30d', '60d', '3mo', '6mo', '1y', '2y', '5y',
                     '10y', 'ytd', 'max']
    INTERVAL_UNITS = ['m', 'h', 'd', 'wk', 'mo', 'y']
    VALID_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h',
                       '1d', '5d', '1wk', '1mo', '3mo']
    DEFAULT_INTERVALS = {'1d': '1m', '7d': '1m', '60d': '2m', '1mo': '2m',
                         '3mo': '60m', '6mo': '60m', 'ytd': '60m', '1y': '60m',
                         '2y': '60m', '5y': '1d', '10y': '1d', 'max': '1d'}

    @classmethod
    def get_history(
            cls, symbol: str, period='60d', interval=DEFAULT_INTERVALS['60d'],
            start: str = None, end: str = None, rounding=2, source=SOURCES[0]):
        """Gets `symbol` price history from `source`.

        Parameters:
            symbol (any): Stock symbol.
            period (str): Period to latest quote. See `MAX_PERIODS`.
            interval (str): Data intervals. See `VALID_INTERVALS`.
            start (str): Date indicating period start.
            end (str): Date indicating period end.
            rounding (int): Number of significant digits in decimal.
            source (str): Data source. See `SOURCES`.

        Returns:
            pd.DataFrame containing history or None if there was a problem
            pulling the data.
        """
        # Validates `period`.
        match = re.match(r'([0-9]*)(d|wk|mo|y|ytd|max)', period)
        if not match:
            raise ValueError(f'period={period} is not valid! '
                             "Valid window: '{n}d', '{n}wk', '{n}mo', '{n}y', "
                             "'ytd', 'max'")

        # Validates `interval`.
        match = re.match(r'([0-9]*)(m|h|d|wk|mo)', interval)
        if not match:
            raise ValueError(f'interval={interval} is not valid! '
                             "Valid intervals: '{n}m', '{n}h', '{n}d', '{n}wk',"
                             " '{n}d', '{n}mo'")

        # Validates `sources`.
        if source not in cls.SOURCES:
            raise ValueError(
                f'source = {value} is not valid!'
                f'\nValid sources are: {cls.SOURCES}'
            )

        if source == 'yfinance':
            return cls._get_history_yf(
                symbol, period, interval, start, end, rounding)
        elif source == 'iex':
            return cls._get_history_iex()

    @classmethod
    def _get_history_yf(
            cls, symbol: str, period='60d', interval=DEFAULT_INTERVALS['60d'],
            start: str = None, end: str = None, rounding=2):
        """Gets `symbol` price history from Yahoo Finance.

        `prepost` is set to True because yf otherwise does not include 4:00 PM
        quotes. The remaining prepost data is subsequently truncated.
        """
        try:
            history = yf.Ticker(symbol).history(
                period=period, interval=interval, start=start, end=end,
                prepost=True, rounding=rounding)
        except:
            return None

        if history.empty:
            return None

        history = history.drop(columns=['Dividends', 'Stock Splits']).dropna()

        # Truncates prepost data.
        if re.match(r'[0-9]+[mh]$', interval):
            history = history.loc[history.index.time >= dt.time(9, 30)]
            history = history.loc[history.index.time <= dt.time(16)]

        return history

    @classmethod
    def _get_history_iex(cls):
        pass


if __name__ == '__main__':
    pass
