#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- check_defaults.py ---

Checks screens module.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


import config, utils
from screens import Screener


unscreened_txt = f'{config.ASSETS_DIR}/stocks-unscreened.txt'
screened_txt = f'{config.ASSETS_DIR}/stocks-screened.txt'
symbols = utils.txt2symbols(unscreened_txt)


def check_default():
    screened = Screener.screen(symbols)
    Screener.print_summary()
    Screener.export_summary()
    print(f'PASS Symbols = {screened}\n')

    Screener.clear()
    print(Screener.stats)
    print(Screener.results)


def check_maxage():
    screened = Screener.screen(symbols, criteria='MaxAge', max_age=20)
    Screener.print_summary()
    Screener.export_summary()
    print(f'PASS Symbols ({len(screened)}) = {screened}\n')
    utils.symbols2txt(screened, screened_txt)
    print(f"Screened symbols written to '{screened_txt}'.")


def check_bigwaves():
    symbols = utils.txt2symbols(screened_txt)
    screened = Screener.screen(symbols, criteria='BigWaves')
    Screener.print_summary()
    Screener.export_summary()
    print(f'PASS Symbols ({len(screened)}) = {screened}\n')
    utils.symbols2txt(screened, screened_txt)
    print(f"Screened symbols written to '{screened_txt}'.")


if __name__ == '__main__':
    #check_default()
    # The following two functions must be chained!
    #check_maxage()
    check_bigwaves()
