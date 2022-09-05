#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- screens.py ---

Screens stocks according to criteria.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""
import datetime as dt
import textwrap

import dateutil.relativedelta as rd
import numpy as np
import pandas as pd

from stocks import Stock
from statistics import Statistic


class Screener:
    """Screens stocks according to criteria.

    Attributes:
        VALID_CRITERIA (str): Valid name switches for screening logic.
        DESCRIPTIONS (dict): keys=criteria, values=description.
        criteria (str): Active screening criteria.
        stats (pd.DataFrame): Data assembled during screening.
        results (pd.DataFrame): Boolean table indicating pass/fail result of
            screening criteria.
    """
    VALID_CRITERIA = ['Default', 'BigWaves', 'MaxAge']
    DESCRIPTIONS = {
        'Default': textwrap.dedent("""\
            Criteria:
                1. Average monthly price change for period='max' > 0
                2. Average weekly price change for period='1y' > 0
                3. Average daily price change for period='3mo' > 0
                4. Average daily range for period='3mo' > 3%
        """),
        'BigWaves': textwrap.dedent("""\
            Criteria:
                1. %Chg 9:30 - 10:30 > 2.0
                2. %Chg 10:30 - 11:30 > 1.0
                3. %Chg 11:30 - 12:30 > 0.5
                4. Avg. Volume 9:30 - 12:30 > 1M
        """),
        'MaxAge': textwrap.dedent("""\
            Criteria:
                1. Company's age is less than `age`
        """)}
    criteria = VALID_CRITERIA[0]
    stats = None
    results = None

    @classmethod
    def clear(cls):
        """Resets `stats` and `results` to None."""
        cls.stats = None
        cls.results = None
        print('\tCleared Screener.')

    @classmethod
    def screen(cls, symbols: list, criteria=VALID_CRITERIA[0], **kwargs):
        """Returns the symbols that meet the screening criteria."""
        symbols = sorted(set(symbols))
        cls.criteria = criteria

        print(f'=== Screen: {criteria} ===')

        screened = []
        for symbol in symbols:
            print(f'\tScreening {symbol}...')
            mask = cls._judge(symbol, criteria, **kwargs)
            if sum(mask) == len(mask):
                screened.append(symbol)

        return screened

    @classmethod
    def _judge(cls, symbol: str, criteria: str, **kwargs):
        """Sets `stats` and `results` according to screening criteria.

        Returns:
            tuple: Booleans indicating pass/fail result of screening criteria.
        """
        for k, v in kwargs.items():
            if k == 'max_age':
                max_age = v

        mask = []
        if criteria == cls.VALID_CRITERIA[0]:
            # Checks criterion 1.
            stock = Stock(symbol, period='max', interval='1mo')
            if stock.history is not None:
                avg_monthly_chg = stock.history['Low'].pct_change().mean()
                avg_monthly_chg *= 100
            else:
                avg_monthly_chg = np.nan
            crit_1 = avg_monthly_chg > 0

            # Checks criterion 2.
            stock = Stock(symbol, period='1y', interval='1wk')
            if stock.history is not None:
                avg_weekly_chg = stock.history['Low'].pct_change().mean()
                avg_weekly_chg *= 100
            else:
                avg_weekly_chg = np.nan
            crit_2 = avg_weekly_chg > 0

            # Checks criterion 3.
            stock = Stock(symbol, period='3mo', interval='1d')
            if stock.history is not None:
                avg_daily_chg = stock.history['Low'].pct_change().mean()
                avg_daily_chg *= 100
            else:
                avg_daily_chg = np.nan
            crit_3 = avg_daily_chg > 0

            # Checks criterion 4.
            stock = Stock(symbol, period='3mo', interval='60m')
            if stock.history is not None:
                ls = [g[1] for g in stock.history.groupby(
                    stock.history.index.day, sort=False)]
                daily_ranges = []
                for df in ls:
                    am_lows = df[df.index.time <= dt.time(12, 25)]['Low']
                    am_min = am_lows.min()
                    pm_highs = df[df.index.time > dt.time(12, 25)]['High']
                    pm_min = pm_highs.min()
                    daily_ranges.append((pm_min - am_min) / am_min)
                avg_daily_rng = sum(daily_ranges) / len(daily_ranges)
                avg_daily_rng *= 100
            else:
                avg_daily_rng = np.nan
            crit_4 = avg_daily_rng > 3

            cls.stats = pd.concat([cls.stats, pd.DataFrame(
                data={'Avg_Monthly_Chg_(All)': avg_monthly_chg,
                      'Avg_Weekly_Chg_(1y)': avg_weekly_chg,
                      'Avg_Daily_Chg_(3mo)': avg_daily_chg,
                      'Avg_Daily_Rng_(3mo)': avg_daily_rng},
                index=[symbol]).round(2)])
            if not cls.stats.index.name:
                cls.stats.index.name = 'Stock'

            cls.results = pd.concat([cls.results, pd.DataFrame(
                data={'Criterion_1': crit_1, 'Criterion_2': crit_2,
                      'Criterion_3': crit_3, 'Criterion_4': crit_4},
                index=[symbol])])
            if not cls.results.index.name:
                cls.results.index.name = 'Stock'

            mask = (crit_1, crit_2, crit_3, crit_4)

        elif criteria == cls.VALID_CRITERIA[1]:
            stock = Stock(symbol)
            stat = Statistic(stock, what='HourlyChg')

            # Checks criterion 1.
            crit_1 = stat.hourly_pct_chg_1 > 2.0

            # Checks criterion 2.
            crit_2 = stat.hourly_pct_chg_2 > 1.0

            # Checks criterion 3.
            crit_3 = stat.hourly_pct_chg_3 > 0.5

            # Checks criterion 4.
            crit_4 = stat.avg_volume > 1_000_000

            # Set stats.
            cls.stats = pd.concat([cls.stats, pd.DataFrame(
                data={'Hourly_%Chg_1': stat.hourly_pct_chg_1,
                      'Hourly_%Chg_2': stat.hourly_pct_chg_2,
                      'Hourly_%Chg_3': stat.hourly_pct_chg_3,
                      'Avg_Volume': stat.avg_volume},
                index=[symbol])])
            if not cls.stats.index.name:
                cls.stats.index.name = 'Stock'

            # Set results.
            cls.results = pd.concat([cls.results, pd.DataFrame(
                data={'Criterion_1': crit_1,
                      'Criterion_2': crit_2,
                      'Criterion_3': crit_3,
                      'Criterion_4': crit_4},
                index=[symbol])])
            if not cls.results.index.name:
                cls.results.index.name = 'Stock'

            mask = (crit_1, crit_2, crit_3, crit_4)

        elif criteria == cls.VALID_CRITERIA[2]:
            stock = Stock(symbol, period='max', interval='1d')

            # Checks criterion 1.
            date_0 = stock.history.index[0]
            date_1 = dt.datetime.today()
            diff_in_years = rd.relativedelta(date_1, date_0).years

            crit_1 = diff_in_years <= max_age

            mask = (crit_1,)

        return mask

    @classmethod
    def print_summary(cls):
        pd.set_option('display.max_rows', None, 'display.max_columns', None)
        print(cls.DESCRIPTIONS[cls.criteria])
        print('--- Stats ---')
        print(cls.stats, '\n')
        print('--- Results ---')
        print(cls.results, '\n')
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')

    @classmethod
    def export_summary(cls, dir='.', fname='screen'):
        if cls.stats is not None:
            today = dt.datetime.today().strftime('%Y-%m-%d')
            pathout = f'{dir}/{fname}_{today}.txt'
            with open(pathout, 'w') as fh:
                fh.write('--- Stats ---\n')
                Screener.stats.to_string(fh)
                fh.write('\n\n')
                fh.write('--- Results ---\n')
                Screener.results.to_string(fh)
            print(f"Exported results to '{pathout}'.")
        else:
            print('No `stats` or `results` to export.')


if __name__ == '__main__':
    pass
