import os
from dotenv import load_dotenv
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import talib  # pip install TA-Lib  (or use pandas-ta if TA-Lib is hard to install)

load_dotenv()
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

if not API_KEY:
    raise ValueError("ALPHAVANTAGE_API_KEY not found in .env")

ts = TimeSeries(key=API_KEY, output_format='pandas')

symbol = 'NVDA'

print(f"Fetching daily data for {symbol}...\n")

try:
    # Single API call for daily data (last 100 days is enough)
    data, meta = ts.get_daily(symbol=symbol, outputsize='compact')
    
    df = data.copy()
    df = df.sort_index(ascending=True)  # oldest to newest
    
    # Calculate indicators locally
    df['RSI'] = talib.RSI(df['4. close'], timeperiod=14)
    macd, macd_signal, macd_hist = talib.MACD(df['4. close'], 
                                              fastperiod=12, 
                                              slowperiod=26, 
                                              signalperiod=9)
    df['MACD'] = macd
    df['MACD_Signal'] = macd_signal
    df['MACD_Hist'] = macd_hist

    # Last 20 trading days, most recent first
    recent = df.tail(20).iloc[::-1]

    print(f"RSI & MACD for {symbol} - Last 20 Trading Days (1 API call only)")
    print(recent[['RSI', 'MACD', 'MACD_Signal', 'MACD_Hist']].round(4))

    latest = recent.iloc[0]
    print("\n" + "="*60)
    print("LATEST VALUES:")
    print(f"RSI (14)       : {latest['RSI']:.2f}")
    print(f"MACD           : {latest['MACD']:.4f}")
    print(f"MACD Signal    : {latest['MACD_Signal']:.4f}")
    print(f"MACD Histogram : {latest['MACD_Hist']:.4f}")
    print("="*60)

except Exception as e:
    print(f"Error: {e}")