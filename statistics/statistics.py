#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- statistics.py ---

Contains class definition for stocks statistics.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


import pandas as pd

from stocks import Stock
from collector import Collector


class Statistic:
    """Data derived from stock history.

    Calculates `what` statistic and adds it to `stock` `statistics` (dict)
    attribute. If `statistics` attribute doesn't exist, it will be created.

    Args:
        stock (Stock): Stock to calculate statistic from and attach to.
        what (str): Acts as switch for calculation. Restricted by `VALID_WHATS`.
        metadata (str): Additional data to include.
        **kwargs: Informal keyword arguments. Passed to `calculate` method.

    Attributes:
        VALID_WHATS (list): Valid types of statistics.
        data (pd.DataFrame): The calculated statistic.
    """

    VALID_WHATS = ['FirstN', 'VolRSI', 'Gobo', 'SimpleRSI', 'HourlyChg']

    def __init__(self, stock: Stock, what: str, metadata='', **kwargs):
        self._stock = None
        self.stock = stock
        self.what = what
        self.metadata = metadata
        self.data = None

        self.calculate(self.stock, what, **kwargs)

    def __str__(self):
        pd.set_option('display.max_rows', None, 'display.max_columns', None)
        string = (f'=== {self.what} ===\n'
                  f'--- Metadata ---\n'
                  f'{self.metadata}\n'
                  f'--- Data ---\n'
                  f'{self.data}\n')
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')

        return string


    @property
    def stock(self):
        """stock (Stock): Stock to get statistics from."""
        return self._stock

    @stock.setter
    def stock(self, value):
        """Ensures the following:
            1. `value` is a `Stock` object or `None`.
            2. History is available or it can be made available by reducing the
               `period` attribute of `value`.
        """
        print(f'Processing stock...')
        stock = value
        if not isinstance(stock, Stock):
            raise TypeError('`stock` must be a `Stock` object!')
        if stock.history is None:
            start = Collector.VALID_PERIODS.index(stock.period) - 1
            if start < 0:
                self._stock = None
                return
            while(stock.history is None and start >= 0):
                print(f"\tResetting {stock.symbol} period to '"
                      f"{Collector.VALID_PERIODS[start]}'...")
                stock.period = Collector.VALID_PERIODS[start]
                stock.refresh()
                start -= 1
            if stock.history is None:
                self._stock = None
                return
        self._stock = stock
        print(f'\tDone.\n')

    def calculate(self, stock: Stock, what: str, **kwargs):
        """Sets `data` to results from `what` statistic calculation."""
        if what not in self.VALID_WHATS:
            raise ValueError(f'Invalid $what={what}! Hint: {self.VALID_WHATS}')

        if what == 'FirstN':
            self.data = self._calculate_firstn(stock, **kwargs)
        elif what == 'VolRSI':
            self.data = self._calculate_volrsi(stock, **kwargs)
        elif what == 'SimpleRSI':
            self.data = self._calculate_simplersi(stock, **kwargs)
        elif what == 'Gobo':
            self.data = self._calculate_gobo(stock, **kwargs)
        elif what == 'HourlyChg':
            self.data = self._calculate_hourlychg(stock, **kwargs)

        if not hasattr(stock, 'statistics'):
            setattr(stock, 'statistics', {})
        stock.statistics[what] = self

    def _calculate_firstn(self, stock: Stock, **kwargs):
        """Calculates market-open to `n`th interval statistics.

        Args:
            stock (Stock): Stock instance with non-empty `history`.
            **kwargs: Informal keyword arguments. The following are parsed:
                n (int): nth interval since market-open.

        Returns:
            pd.DataFrame: Data for assessing market-open trades.

            indexes: Date, Time
            columns: Event, %Vol, RSI, %Chg
        """
        print('Calculating FirstN...')

        if 'RSI' not in stock.indicators:
            print('\tERROR: $stock does not have RSI indicator!')
            return None

        # Defaults.
        n = 9

        # Parses `kwargs`.
        for k, v in kwargs.items():
            if k == 'n':
                n = v

        h = stock.history.groupby(
            stock.history.index.date, sort=False).head(n).dropna()
        g = h.groupby(h.index.date, sort=False)

        # Adds Event column to `h`.
        h.loc[g['RSI'].idxmin(), 'Event'] = ''
        h.loc[g['Low'].idxmin(), 'Event'] = ''
        h.loc[g['RSI'].idxmax(), 'Event'] = ''
        h.loc[g['Low'].idxmax(), 'Event'] = ''
        h.loc[g['RSI'].idxmin(), 'Event'] += 'MinRSI '
        h.loc[g['Low'].idxmin(), 'Event'] += 'MinPrice '
        h.loc[g['RSI'].idxmax(), 'Event'] += 'MaxRSI '
        h.loc[g['Low'].idxmax(), 'Event'] += 'MaxPrice '

        # Makes Event column pretty.
        h['Event'].fillna('', inplace=True)
        h['Event'] = h['Event'].astype(str).apply(lambda s: s.strip())

        # Adds %Vol column to `h`.
        max_open_vol = g['Volume'].first().max()
        h['%Vol'] = (h['Volume'] / max_open_vol * 100).round(2)

        # Adds %Chg column to `h`.
        for i, df in g:
            open_price = df['Open'].iloc[0]
            h.loc[df.index, '%Chg'] = (
                    (df['Low'] - open_price) / open_price * 100).round(2)

        # Removes excess data.
        h = h[['Event', '%Vol', 'RSI', '%Chg']]
        h = h.groupby([h.index.date, h.index.time], sort=False).first()
        h.index.set_names(['Date', 'Time'], inplace=True)

        return h

    def _calculate_volrsi(self, stock: Stock):
        """Calculates RSI profitability statistics.

        Args:
            stock (Stock): Stock instance with non-empty `history`.

        Returns:
            pd.DataFrame: Data for assessing RSI profitability.

            indexes: VolLvl, RSI
            columns: %All, %Neg, %Pos, %Loss, %Gain
        """
        print('Calculating VolRSI...')

        if 'RSI' not in stock.indicators:
            print('\tERROR: $stock does not have RSI indicator!')
            return None

        self.metadata += f'Symbol: {stock.symbol}\n'
        self.metadata += f'Period: {stock.period}\n'
        self.metadata += f'Interval: {stock.interval}\n'

        h = stock.history.dropna().copy()
        h['RSI'] = h['RSI'].round(0).astype(int)
        g = h.groupby(h.index.date, sort=False)

        # Adds VolLvl column to `h`.
        q1 = int(h['Volume'].quantile(q=0.80))
        q2 = int(h['Volume'].quantile(q=0.90))
        h.loc[h[h['Volume'] <= q1].index, 'VolLvl'] = 'Low'
        h.loc[h[(h['Volume'] > q1)
                & (h['Volume'] < q2)].index, 'VolLvl'] = 'Medium'
        h.loc[h[h['Volume'] >= q2].index, 'VolLvl'] = 'High'
        self.metadata += f'Low Vol: Vol <= {q1}\n'
        self.metadata += f'Medium Vol: {q1} < Vol < {q2}\n'
        self.metadata += f'High Vol: Vol >= {q2}\n'

        def func(df: pd.DataFrame):
            """Returns `df` plus %Chg, %Neg, %Pos, %Gain, %Loss columns."""
            rsi_min = df['RSI'].min()
            rsi_max = df['RSI'].max()
            for rsi in range(rsi_min, rsi_max + 1):
                idx = df[df.RSI == rsi].first_valid_index()
                if idx is None:
                    continue
                price = df.loc[idx, 'Low']
                sub = df.loc[idx:]
                sub['%Chg'] = ((sub['Low'] - price) / price * 100).round(2)
                df.loc[idx, '%Neg'] = round(
                    len(sub['%Chg'][sub['%Chg'] <= 0]) / len(sub) * 100, 2)
                df.loc[idx, '%Pos'] = round(
                    len(sub['%Chg'][sub['%Chg'] > 0]) / len(sub) * 100, 2)
                df.loc[idx, '%Loss'] = round(
                    sub['%Chg'][sub['%Chg'] <= 0].min(), 2)
                df.loc[idx, '%Gain'] = round(
                     sub['%Chg'][sub['%Chg'] > 0].max(), 2)
            return df

        h = g.apply(func).dropna()

        result = pd.DataFrame(
            index=pd.MultiIndex.from_product(
                (['Low', 'Medium', 'High'], sorted(h['RSI'].drop_duplicates())),
                names=['VolLvl', 'RSI']),
            columns=['%All', '%Neg', '%Pos', '%Loss', '%Gain']
        )

        g = h.groupby([h['VolLvl'], h['RSI']])
        for i, df in g:
            result.loc[i, '%All'] = round(len(df) / len(h) * 100, 2)
        result['%Neg'] = g['%Neg'].mean()
        result['%Pos'] = g['%Pos'].mean()
        result['%Loss'] = g['%Loss'].mean()
        result['%Gain'] = g['%Gain'].mean()
        result = result.dropna().round(2)

        return result

    def _calculate_simplersi(self, stock: Stock):
        """Calculates simple RSI profitability statistics.

        Args:
            stock (Stock): Stock instance with non-empty `history`.

        Returns:
            pd.DataFrame: Data for assessing RSI profitability.

            index: RSI
            columns: %All, %Neg, %Pos, %Loss, %Gain
        """
        print('Calculating SimpleRSI...')

        if 'RSI' not in stock.indicators:
            print('\tERROR: $stock does not have RSI indicator!')
            return None

        self.metadata += f'Symbol: {stock.symbol}\n'
        self.metadata += f'Period: {stock.period}\n'
        self.metadata += f'Interval: {stock.interval}\n'

        h = stock.history.dropna().copy()
        h['RSI'] = h['RSI'].round(0).astype(int)
        g = h.groupby(h.index.date, sort=False)

        def func(df: pd.DataFrame):
            """Returns `df` plus %Chg, %Neg, %Pos, %Gain, %Loss columns."""
            rsi_min = df['RSI'].min()
            rsi_max = df['RSI'].max()
            for rsi in range(rsi_min, rsi_max + 1):
                idx = df[df.RSI == rsi].first_valid_index()
                if idx is None:
                    continue
                price = df.loc[idx, 'Low']
                sub = df.loc[idx:]
                sub['%Chg'] = ((sub['Low'] - price) / price * 100).round(2)
                df.loc[idx, '%Neg'] = round(
                    len(sub['%Chg'][sub['%Chg'] <= 0]) / len(sub) * 100, 2)
                df.loc[idx, '%Pos'] = round(
                    len(sub['%Chg'][sub['%Chg'] > 0]) / len(sub) * 100, 2)
                df.loc[idx, '%Loss'] = round(
                    sub['%Chg'][sub['%Chg'] <= 0].min(), 2)
                df.loc[idx, '%Gain'] = round(
                     sub['%Chg'][sub['%Chg'] > 0].max(), 2)
            return df

        h = g.apply(func).dropna()

        result = pd.DataFrame(
            index=sorted(h['RSI'].drop_duplicates()),
            columns=['%All', '%Neg', '%Pos', '%Loss', '%Gain']
        )
        result.index.name = 'RSI'

        g = h.groupby(h['RSI'])
        for i, df in g:
            result.loc[i, '%All'] = round(len(df) / len(h) * 100, 2)
        result['%Neg'] = g['%Neg'].mean()
        result['%Pos'] = g['%Pos'].mean()
        result['%Loss'] = g['%Loss'].mean()
        result['%Gain'] = g['%Gain'].mean()
        result = result.dropna().round(2)

        return result

    def _calculate_gobo(self, stock: Stock, **kwargs):
        """Calculates %Chg per open avg_volume for good and bad days.

        Args:
            stock (Stock): Stock instance with non-empty `history`.
            **kwargs: Informal keyword arguments. The following are parsed:
                n (int): nth interval since market-open.

        Returns:
            pd.DataFrame: Data for assessing market-open trades.

            indexes: Date, Time
            columns: Event, %Vol, RSI, %Chg
        """
        print('Calculating Gobo...')

        self.metadata += f'Symbol: {stock.symbol}\n'
        self.metadata += f'Period: {stock.period}\n'
        self.metadata += f'Interval: {stock.interval}\n'

        # Defaults.
        n = 9

        # Parses `kwargs`.
        for k, v in kwargs.items():
            if k == 'n':
                n = v

        h = stock.history.dropna().copy()
        h = h.groupby(h.index.date, sort=False).head(n)
        g = h.groupby(h.index.date, sort=False)

        def func(df: pd.DataFrame):
            """Adds OpenIs, OpenVol %Down and %Up columns to `df`."""
            # Sets OpenIs column.
            if df['Close'].pct_change().mean() > 0:
                df['OpenIs'] = 'Good'
            else:
                df['OpenIs'] = 'Bad'

            # Sets OpenVol column.
            df['OpenVol'] = df.iloc[0]['Volume'].astype(int)
            df['%Down'] = df['Low'][1:].min() - df['Low'][0]
            df['%Up'] = df['Low'][1:].max() - df['Low'][0]
            return df

        h = g.apply(func)
        h = h[['OpenIs', 'OpenVol', '%Down', '%Up']].drop_duplicates('OpenVol')
        h.sort_values(['OpenIs', 'OpenVol'], inplace=True)
        h.set_index(['OpenIs', 'OpenVol'], inplace=True)
        return  h


    def _calculate_hourlychg(self, stock: Stock):
        print('Calculating HourlyChg...')

        self.metadata += f'Symbol: {stock.symbol}\n'
        self.metadata += f'Period: {stock.period}\n'
        self.metadata += f'Interval: {stock.interval}\n'

        # Defaults.
        if stock.interval == '1m':
            n = 181
            n_per_hr = 60
        elif stock.interval == '2m':
            n = 91
            n_per_hr = 30
        elif stock.interval == '5m':
            n = 37
            n_per_hr = 12
        elif stock.interval == '10m':
            n = 19
            n_per_hr = 6
        elif stock.interval == '15m':
            n = 13
            n_per_hr = 4
        elif stock.interval == '30m':
            n = 7
            n_per_hr = 2
        elif stock.interval == '60m':
            n = 4
            n_per_hr = 1

        h = stock.history.groupby(stock.history.index.date, sort=False).head(n)
        g = h.groupby(h.index.date, sort=False)

        # Initialize result-holding vars.
        dates = []
        hourly_pct_chg_1 = []
        hourly_pct_chg_2 = []
        hourly_pct_chg_3 = []
        vol_cumm = []

        # Calculate hourly_pct_chg and vol_cumm.
        for dt, df in g:
            dates.append(dt)

            start = 0
            end = n_per_hr + 1
            low_min = df['Low'][start:end].min()
            low_max = df['Low'][start:end].max()
            hourly_pct_chg_1.append(abs(1 - low_max / low_min) * 100)

            start = end - 1
            end = end + n_per_hr + 1
            low_min = df['Low'][start:end].min()
            low_max = df['Low'][start:end].max()
            hourly_pct_chg_2.append(abs(1 - low_max / low_min) * 100)

            start = end - 1
            end = end + n_per_hr + 1
            low_min = df['Low'][start:end].min()
            low_max = df['Low'][start:end].max()
            hourly_pct_chg_3.append(abs(1 - low_max / low_min) * 100)

            vol_cumm.append(df['Volume'][0:end].sum())

        # Return result as Dataframe.
        result = pd.DataFrame(
            index=dates,
            data={'%Chg1': hourly_pct_chg_1,
                  '%Chg2': hourly_pct_chg_2,
                  '%Chg3': hourly_pct_chg_3,
                  'Volume': vol_cumm
            })
        result = result.round(2)

        # Add additional metadata.
        self.hourly_pct_chg_1 = result['%Chg1'].mean().round(2)
        self.hourly_pct_chg_2 = result['%Chg2'].mean().round(2)
        self.hourly_pct_chg_3 = result['%Chg3'].mean().round(2)
        self.avg_volume = result['Volume'].mean().astype(int)
        self.metadata += f"Avg %Chg1: {self.hourly_pct_chg_1}\n"
        self.metadata += f"Avg %Chg2: {self.hourly_pct_chg_2}\n"
        self.metadata += f"Avg %Chg3: {self.hourly_pct_chg_3}\n"
        self.metadata += f"Avg Volume: {self.avg_volume}\n"

        return result


if __name__ == '__main__':
    pass
