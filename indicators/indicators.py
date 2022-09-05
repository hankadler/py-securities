#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- indicators_remaining.py ---

Relative Strength Index.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


import pandas as pd


class Indicators:
    INDICATORS = ['RSI']

    @staticmethod
    def RSI(prices: pd.Series, window: int):
        """Calculates RSI(`window`) on `prices`.

        Parameters:
            prices (pd.Series): Stock price history.
            window (int): Window size for rolling operations.

        Returns:
            pd.Series: index=Datetime, columns=RSI
        """
        changes = prices.pct_change()

        gains = changes.copy()
        gains[changes <= 0] = 0.0

        losses = abs(changes.copy())
        losses[changes > 0] = 0.0

        avg_gain = gains.rolling(window).mean()
        avg_loss = losses.rolling(window).mean()

        return (100 - 100 / (1 + avg_gain / avg_loss)).__round__(2)


if __name__ == '__main__':
    pass
