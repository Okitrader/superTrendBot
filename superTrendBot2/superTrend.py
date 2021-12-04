import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
#pd.set_option('display.max_rows', None)
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
    df['upper_band'] = hl2 + (multiplier * df['atr'])
    df['lower_band'] = hl2 - (multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)): # creates a current variable that iterates over the index of the dataframe
        previous = current - 1 # previous is the current minus the last value

        if df.iloc[current]['close'] > df.iloc[previous]['upper_band']: # if current close is above upper band
            df['in_uptrend'].iloc[current] = True # set in_uptrend to True
        elif df.iloc[current]['close'] < df.iloc[previous]['lower_band']: # if current close is below lower band
            df['in_uptrend'].iloc[current] = False # set in_uptrend to False
        else:
            df['in_uptrend'].iloc[current] = df['in_uptrend'].iloc[previous] # the trend is the same as the previous trend

            if df['in_uptrend'][current] and df['lower_band'][current] < df['lower_band'][previous]: # if in uptrend and lower band is below previous lower band
                df['lower_band'].iloc[current] = df['lower_band'].iloc[previous] # set lower band to previous lower band

            if not df['in_uptrend'][current] and df['upper_band'][current] > df['upper_band'][previous]: # if in downtrend and upper band is above previous upper band
                df['upper_band'].iloc[current] = df['upper_band'].iloc[previous] # set upper band to previous upper band


    print(df)

supertrend(df)

