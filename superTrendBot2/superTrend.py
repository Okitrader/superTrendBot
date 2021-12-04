import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

exchange = ccxt.binance()
bars = exchange.fetch_ohlcv('ETH/USDT', timeframe='1d', limit=200)
df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr

def atr(data, period=14):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr

def supertrend(df, period=7, multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = atr(df, period)
    df['basic_upper_band'] = hl2 + (multiplier * df['atr'])
    df['basic_lower_band'] = hl2 - (multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        prev = current - 1

        if df.iloc[current]['close'] > df.iloc[prev]['basic_upper_band']: # if current close is above upper band
            df['in_uptrend'].iloc[current] = True # set in_uptrend to True
        elif df.iloc[current]['close'] < df.iloc[prev]['basic_lower_band']: # if current close is below lower band
            df['in_uptrend'].iloc[current] = False # set in_uptrend to False
        else:
            df['in_uptrend'].iloc[current] = df['in_uptrend'].iloc[prev] # the trend is the same as the previous trend



    print(df)

supertrend(df)

