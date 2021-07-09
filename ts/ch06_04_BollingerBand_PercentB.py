
import FinanceDataReader as fdr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Investar import Analyzer
from datetime import datetime
from datetime import date
today = date.today()
from dateutil.relativedelta import relativedelta
now = datetime.now()
start_date = now - relativedelta(months=12)
end_date = now - relativedelta(days=1)

def get_daily_price(code, start_date=start_date, end_date=end_date):
    df = fdr.DataReader(code, start_date, end_date) # for last 12 months
    return df

code = 'TLSA'
df = get_daily_price(code)
df = df.rename(columns={'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low',  'Volume': 'volume', 'Change': 'change'})

# mk = Analyzer.MarketDB()
# df = mk.get_daily_price('카카오', '2019-01-02')
  
df['MA20'] = df['close'].rolling(window=20).mean() 
df['stddev'] = df['close'].rolling(window=20).std() 
df['upper'] = df['MA20'] + (df['stddev'] * 2)
df['lower'] = df['MA20'] - (df['stddev'] * 2)
df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])  # ①
df = df[19:]

plt.figure(figsize=(20, 16))
plt.subplot(2, 1, 1)  # ②
plt.plot(df.index, df['close'], color='#0000ff', label='Close')
plt.plot(df.index, df['upper'], 'r--', label = 'Upper band')
plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
plt.plot(df.index, df['lower'], 'c--', label = 'Lower band')
plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')
plt.title(f'{code} Bollinger Band(20 day, 2 std)')
plt.legend(loc='best')

plt.subplot(2, 1, 2)  # ③
plt.plot(df.index, df['PB'], color='b', label='%B')  # ④
plt.grid(True)
plt.legend(loc='best')
plt.show()
