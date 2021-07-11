
import FinanceDataReader as fdr
import os
import pandas as pd
import numpy as np
import time
import yfinance as yf
import warnings
warnings.filterwarnings(action='ignore')

from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from pandas_datareader import data as pdr
from pandas import ExcelWriter

# Variables
now = datetime.now()
start_date = now - relativedelta(years=2)
end_date = now - relativedelta(days=1)

index_name = 'S&P500' # NASDAQ - 'nasdaq'
stocks = fdr.StockListing(index_name)
tickers = stocks['Symbol'].tolist()

exportList = pd.DataFrame(columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])
returns_multiples = []

# Index Returns
index_name = 'US500'
index_df = fdr.DataReader(index_name, start_date, end_date)
index_return = (index_df['Change'] + 1).cumprod()[-1]

filePath='./quants/data/'

# Find top 30% performing stocks (relative to the S&P 500)
for ticker in tickers:
    # Download historical data as CSV for each stock (makes the process faster)
#     df = pdr.get_data_yahoo(ticker, start_date, end_date)
    df = fdr.DataReader(ticker, start_date, end_date)
    df.to_csv(f'{filePath}{ticker}.csv')

    # Calculating returns relative to the market (returns multiple)
    df['Change'] = df['Close'].pct_change()
    stock_return = (df['Change'] + 1).cumprod()[-1]
    
    returns_multiple = round((stock_return / index_return), 2)
    returns_multiples.extend([returns_multiple])
    
    print (f'Ticker: {ticker}; Returns Multiple against S&P 500: {returns_multiple}\n')
    time.sleep(1)

# Creating dataframe of only top 30%
rs_df = pd.DataFrame(list(zip(tickers, returns_multiples)), columns=['Ticker', 'Returns_multiple'])
rs_df['RS_Rating'] = rs_df.Returns_multiple.rank(pct=True) * 100
rs_df = rs_df[rs_df.RS_Rating >= rs_df.RS_Rating.quantile(.70)]
