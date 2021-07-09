
import FinanceDataReader as fdr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Investar import Analyzer
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings(action='ignore')
from mpl_finance import candlestick_ohlc
#from mplfinance.original_flavor import candlestick_ohlc

now = datetime.now()
start_date = now - relativedelta(months=12)
end_date = now - relativedelta(days=1)

def get_daily_price(code, start_date=start_date, end_date=end_date):
    df = fdr.DataReader(code, start_date, end_date) # for last 12 months
    return df

def main(code):
    df = get_daily_price(code)
    df = df.rename(columns={'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low',  'Volume': 'volume', 'Change': 'change'})

    # mk = Analyzer.MarketDB()
    # df = mk.get_daily_price('카카오', '2019-01-02')

    df['MA20'] = df['close'].rolling(window=20).mean() 
    df['stddev'] = df['close'].rolling(window=20).std() 
    df['upper'] = df['MA20'] + (df['stddev'] * 2)
    df['lower'] = df['MA20'] - (df['stddev'] * 2)
    df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])

    df['II'] = (2*df['close']-df['high']-df['low'])/(df['high']-df['low'])*df['volume']
    df['IIP21'] = df['II'].rolling(window=21).sum()/df['volume'].rolling(window=21).sum()*100
    df = df.dropna()

    plt.figure(figsize=(20, 16))
    plt.subplot(3, 1, 1)
    plt.title(f'{code} Bollinger Band(20 day, 2 std) - Reversals')
    plt.plot(df.index, df['close'], 'm', label='Close')
    plt.plot(df.index, df['upper'], 'r--', label ='Upper band')
    plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
    plt.plot(df.index, df['lower'], 'c--', label ='Lower band')
    plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')
    for i in range(0, len(df.close)):
        if df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:       # ①
            plt.plot(df.index.values[i], df.close.values[i], 'r^')  # ②
        elif df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:     # ③
            plt.plot(df.index.values[i], df.close.values[i], 'bv')  # ④
    plt.legend(loc='best')

    plt.subplot(3, 1, 2)
    plt.plot(df.index, df['PB'], 'b', label='%b')
    plt.grid(True)
    plt.legend(loc='best')

    plt.subplot(3, 1, 3)
    plt.bar(df.index, df['IIP21'], color='g', label='II% 21day')
    for i in range(0, len(df.close)):
        if df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:
            plt.plot(df.index.values[i], 0, 'r^') # ⑤
        elif df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:
            plt.plot(df.index.values[i], 0, 'bv') # ⑥
    plt.grid(True)
    plt.legend(loc='best')
    plt.show()
    
if __name__=="__main__":
    code = 'NFLX' # AAPL' # 'AMZN' # 'FB' # 'MSFT' # 'NVDA' # 'PYPL' # 'MRNA'
    main(code)
