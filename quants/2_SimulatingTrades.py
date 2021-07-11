
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from pandas_datareader import data as pdr

yf.pdr_override()
now = datetime.now()
start_date = now - relativedelta(years=2)
end_date = now - relativedelta(days=1)

stock = input("Enter a stock ticker symbol: ")
df = fdr.DataReader(stock, start_date, end_date) # for last 12 months
df = df.rename(columns={'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low',  'Volume': 'volume', 'Change': 'change'})

# ma=50
# smaString="Sma_"+str(ma)
# df[smaString]=df.iloc[:,4].rolling(window=ma).mean()

emasUsed = [3,5,8,10,12,15,30,35,40,45,50,60]
for x in emasUsed:
    ema = x
    df['EMA_'+str(ema)] = round(df.iloc[:, 0].ewm(span=ema,adjust=False).mean(),20)

df = df.iloc[60:]

# print(df)

pos = 0
percentchange = []
num = 0
for i in df.index:
    emasUsed = [3,5,8,10,12,15,30,35,40,50,60]
    cmin=min(df['EMA_3'][i],df['EMA_5'][i],df['EMA_8'][i],df['EMA_10'][i],df['EMA_12'][i],df['EMA_15'][i])
    cmax=max(df['EMA_30'][i],df['EMA_35'][i],df['EMA_40'][i],df['EMA_45'][i],df['EMA_50'][i],df['EMA_60'][i])

    close = df['close'][i]
    if((cmin>cmax)):
#         print("Red Write Blue")
        if(pos==0):
            bp=close
            pos=1
            print("Buying now at "+str(bp))
    elif(cmin<cmax):
#         print("Blue Write Red")
        if(pos==1):
            pos=0
            sp=close
            print("Selling now at "+str(sp))
            pc=(sp/bp-1)*100
            percentchange.append(pc)
          
    if(num==df['close'].count()-1 and pos ==1):
        pos=0
        sp=close
        print("Selling now at "+str(sp))
        pc=(sp/bp-1)*100
        percentchange.append(pc)
        
    num+=1
# print(percentchange)

gains=0
ng=0
losses=0
nl=0
totalR=1

for i in percentchange:
    if(i>0):
        gains+=i
        ng+=1
    else:
        losses+=i
        nl+=1
    totalR=totalR*((i/100)+1)
totalR=round((totalR-1)*100, 2)

if(ng>0):
    avgGain=gains/ng
    maxR=str(max(percentchange))
else:
    avgGain=0
    maxR='undefined'

if(nl>0):
    avgLoss=losses/nl
    maxL=str(min(percentchange))
    ratio=str(-avgGain/avgLoss)
else:
    avgLoss=0
    maxL='undefined'
    ratio='inf'
    
if(ng>0 or nl>0):
    battingAvg=ng/(ng+nl)
else:
    battingAvg=0

print()
print("Results for "+ stock +" going back to "+str(df.index[0])+", Sample size: "+str(ng+nl)+" trades")
print("EMAs used: "+str(emasUsed))
print("Batting Avg: "+ str(battingAvg))
print("Gain/Loss ratio: "+ ratio)
print("Average Gain: "+ str(avgGain))
print("Average Loss: "+ str(avgLoss))
print("Max Return: "+ maxR)
print("Max Loss: "+ maxL)
print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR) + "%")
print()
