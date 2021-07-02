import pandas as pd
print(pd.__version__)

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()

data = pdr.get_data_yahoo("PLTR")
# data = pdr.get_data_yahoo("PLTR", start='2020-09-01', end='2021-03-30')

print(data.tail())