#! /usr/bin/env python3

import os

import config, utils


txt_ = f'{config.ASSETS_DIR}/stocks-unscreened.txt'


def check_txt2symbols():
    symbols = utils.txt2symbols(txt_)
    print(symbols)


def check_symbols2txt():
    symbols = utils.txt2symbols(txt_)
    utils.symbols2txt(symbols, 'symbols.txt')
    print("Symbols written to 'symbols.txt'.")


def check_symbols2watchlist():
    symbols = utils.txt2symbols(txt_)
    watchlist_by_index = utils.symbols2watchlist(symbols, 16)
    print(watchlist_by_index)


if __name__ == '__main__':
    # check_txt2symbols()
    # check_symbols2txt()
    check_symbols2watchlist()
