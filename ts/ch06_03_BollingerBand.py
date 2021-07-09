
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

code = 'GOOGL'
df = get_daily_price(code)
df = df.rename(columns={'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low',  'Volume': 'volume', 'Change': 'change'})
  
df['MA20'] = df['close'].rolling(window=20).mean()  # ①
df['stddev'] = df['close'].rolling(window=20).std() # ②
df['upper'] = df['MA20'] + (df['stddev'] * 2)   # ③
df['lower'] = df['MA20'] - (df['stddev'] * 2)   # ④
df = df[19:]  # ⑤

plt.figure(figsize=(20, 16))
plt.plot(df.index, df['close'], color='#0000ff', label='Close')    # ⑥
plt.plot(df.index, df['upper'], 'r--', label = 'Upper band')       # ⑦
plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
plt.plot(df.index, df['lower'], 'c--', label = 'Lower band')
plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')  # ⑧ 
plt.legend(loc='best')
plt.title(f'{code} Bollinger Band (20 day, 2 std)')
plt.show()
