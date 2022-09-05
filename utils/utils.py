def txt2symbols(path: str) -> list:
    with open(path, 'r') as f:
        symbols = [line.strip('\n') for line in f.readlines()]
    return sorted(symbols)


def symbols2txt(symbols: list, path: str):
    with open(path, 'w', newline='\n') as f:
        for s in symbols:
            f.write(s + '\n')


def symbols2watchlist(symbols: list, size: int) -> dict:
    ls = []
    watchlist_by_index = {}
    i = 0
    j = 0
    count = 0
    for symbol in symbols:
        ls.append(symbol)
        j += 1
        count += 1
        if count == size or j == len(symbols):
            watchlist_by_index[i] = ls.copy()
            ls = []
            i += 1
            count = 0
    return watchlist_by_index
