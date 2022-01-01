import ccxt
import config
import schedule
import pandas as pd
pd.set_option('display.max_rows', None) # display all rows in dataframe; can be

import warnings
warnings.filterwarnings('ignore') # ignore warnings

import numpy as np
from datetime import datetime
import time

exchange = ccxt.coinbasepro({
    "apiKey": config.COINBASEPRO_API_KEY,
    "secret": config.COINBASEPRO_SECRET_KEY,
    "passphrase": config.COINBASEPRO_PASSPHRASE
})

def true_range(data):
    data['previous_close'] = data['close'].shift(1)# shift the close column by 1 creates a previous close column
    data['high-low'] = abs(data['high'] - data['low']) #calculates the abs  high minus low column
    data['high-previous_close'] = abs(data['high'] - data['previous_close']) #calculates the abs high minus previous close column
    data['low-previous_close'] = abs(data['low'] - data['previous_close'])  #calculates the abs low minus previous close column
    true_range = data[['high-low', 'high-previous_close', 'low-previous_close']].max(axis=1) #list passed into df to get max value

    return true_range

def average_true_range(data, period):
    data['true_range'] = true_range(data) # adds the above true range columns to the dataframe
    the_atr = data['true_range'].rolling(period).mean() # calculates the average true range over 14 bars

    return the_atr

def super_trend(df, period=7, atr_multiplier=3): # adapted from https://www.tradingfuel.com/supertrend-indicator-formula-and-calculation/
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = average_true_range(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True # sets the in_uptrend column to true

    for current in range(1, len(df.index)):  # iterate through the dataframe
        previous = current - 1  # creates a variable for the previous index value

        if df['close'][current] > df['upperband'][previous]:  # if the current close is greater than the upper band
            df['in_uptrend'][current] = True  # set the in_uptrend column to true
        elif df['close'][current] < df['lowerband'][previous]: # if the current close is less than the lower band
            df['in_uptrend'][current] = False # set the in_uptrend column to false
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]  # if the current close is between the upper and lower band, set the in_uptrend column to the previous value

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:  # if the current close is greater than the lower band and the in_uptrend column is true
                df['lowerband'][current] = df['lowerband'][previous]  # set the lower band to the previous lower band

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:  # if the current close is less than the upper band and the in_uptrend column is false
                df['upperband'][current] = df['upperband'][previous]  # set the upper band to the previous upper band


    return df

def check_buy_signal(df):
    print('Checking buy and sell signals')
    print(df.tail(2))
    last_row = df.iloc[-1]
    previous_row = last_row - 1

    print(last_row)
    print(previous_row)

    if not df['in_uptrend'][previous_row] and df['in_uptrend'][last_row]:  # if the previous close is not in the uptrend and the current close is in the uptrend
        print('Buy signal detected')

    if df['in_uptrend'][previous_row] and not df['in_uptrend'][last_row]:  # if the previous close is in the uptrend and the current close is not in the uptrend
        print('Sell signal detected')

def run_bot():
    crypto = 'ETH/USD'
    print(f'Getting ohlcv data for ' + crypto + ' {datetime.now().isoformat()}')

    bars = exchange.fetch_ohlcv(crypto, timeframe='1m', limit=5)  # fetch the bars for limit time
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)  # set index to timestamp
    df.index = df.index.tz_localize('Asia/Tokyo')# convert the timestamp to Tokyo time
    #print(df)

    supertrend_data = super_trend(df)
    print(supertrend_data)

schedule.every(5).seconds.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)






