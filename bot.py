import ccxt
import ta
import pandas as pd
import config
import schedule
from ta.volatility import BollingerBands, AverageTrueRange

exchange = ccxt.coinbasepro({
    'apiKey': config.COINBASEPRO_API_KEY,
    'secret': config.COINBASEPRO_SECRET_KEY
})

bars = exchange.fetch_ohlcv('BTC/USD', '1h', limit=21)

df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

bb_indicator = BollingerBands(df['close'])

df['upper_band'] = bb_indicator.bollinger_hband()
df['lower_band'] = bb_indicator.bollinger_lband()
df['moving_average'] = bb_indicator.bollinger_mavg()


atr_indicator = AverageTrueRange(df['high'], df['low'], df['close'])

df['atr'] = atr_indicator.average_true_range()

print(df)
