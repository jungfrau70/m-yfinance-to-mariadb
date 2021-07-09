
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

stocks = ['GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'FB', 'NFLX', 'AAPL', 'ZM', 'CRNC', 'COIN', 'PLTR']
df = pd.DataFrame()
for s in stocks:
    df[s] = get_daily_price(s)['Close']
    
# mk = Analyzer.MarketDB()
# stocks = ['삼성전자', 'SK하이닉스', 'LG화학', 'NAVER', '현대자동차', '삼성SDI' , '셀트리온', '카카오', '기아', '현대모비스']
# # stocks = ['GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'FB', 'NFLX', 'APPL', 'MRDA', 'CRNC', 'RE', 'PLTR']
# df = pd.DataFrame()
# for s in stocks:
#     df[s] = mk.get_daily_price(s, '2018-05-04', '2021-07-05')['close']
  
daily_ret = df.pct_change() 
annual_ret = daily_ret.mean() * 252
daily_cov = daily_ret.cov() 
annual_cov = daily_cov * 252

port_ret = [] 
port_risk = [] 
port_weights = [] 

for _ in range(20000): 
    weights = np.random.random(len(stocks)) 
    weights /= np.sum(weights) 

    returns = np.dot(weights, annual_ret) 
    risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights))) 

    port_ret.append(returns) 
    port_risk.append(risk) 
    port_weights.append(weights) 

portfolio = {'Returns': port_ret, 'Risk': port_risk} 
for i, s in enumerate(stocks): 
    portfolio[s] = [weight[i] for weight in port_weights] 
df = pd.DataFrame(portfolio) 
df = df[['Returns', 'Risk'] + [s for s in stocks]] 

df.plot.scatter(x='Risk', y='Returns', figsize=(20, 16), grid=True)
plt.title('Efficient Frontier') 
plt.xlabel('Risk') 
plt.ylabel('Expected Returns') 
plt.show() 
