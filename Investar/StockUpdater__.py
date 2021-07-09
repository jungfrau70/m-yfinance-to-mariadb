
import FinanceDataReader as fdr
import math
import pandas as pd
import pymysql, calendar, time, json
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from threading import Timer

class DBUpdater:  
    def __init__(self):
        """생성자: MariaDB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host='localhost', user='root',
            password='4team123!', db='INVESTAR', charset='utf8')
        
        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info (
                code VARCHAR(20),
                company VARCHAR(80),
                industry VARCHAR(80),
                industryCode VARCHAR(10),                
                last_update DATE,
                PRIMARY KEY (code))
            """
            curs.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS daily_price (
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY (code, date))
            """
            curs.execute(sql)
        self.conn.commit()
        self.codes = dict()
               
    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.conn.close() 
  
    def read_ticker(self):
        """KRX로부터 상장기업 목록 파일을 읽어와서 데이터프레임으로 반환"""
        url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method='\
            'download&searchType=13'
        krx = pd.read_html(url, header=0)[0]
        krx = krx[['종목코드', '회사명']]
        krx = krx.rename(columns={'종목코드': 'code', '회사명': 'company'})
        krx.code = krx.code.map('{:06d}'.format)
        krx['industry'] = ""
        krx['industryCode'] = ""
        stock = fdr.StockListing('NASDAQ')
        stock = stock[['Symbol', 'Name', 'Industry', 'IndustryCode']]
        stock = stock.rename(columns={'Symbol': 'code', 'Name': 'company', 'Industry': 'industry', 'IndustryCode': 'industryCode'})
        stock = stock.replace("\'","\'\'", regex=True)
        df = pd.concat([krx, stock])
        df = df.rename(
            columns={'Symbol': 'code', 'Name': 'company', 'Industry': 'industry', 'IndustryCode': 'industryCode'})
        return df
    
    def update_comp_info(self):
        """종목코드를 company_info 테이블에 업데이트 한 후 딕셔너리에 저장"""
        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, self.conn)
        for idx in range(len(df)):
            self.codes[df['code'].values[idx]] = df['company'].values[idx]
                    
        with self.conn.cursor() as curs:
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            rs = curs.fetchone()
            today = datetime.today().strftime('%Y-%m-%d')
            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
                df = self.read_ticker()
                for idx in range(len(df)):
                    code = df.code.values[idx]
                    company = df.company.values[idx]
                    industry = df.industry.values[idx]
                    industryCode = df.industryCode.values[idx]
                    sql = f"REPLACE INTO company_info (code, company, industry, industryCode, last"\
                        f"_update) VALUES ('{code}', '{company}', '{industry}', '{industryCode}', '{today}')"
                    curs.execute(sql)
                    self.codes[code] = company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] #{idx+1:04d} REPLACE INTO company_info "\
                        f"VALUES ({code}, {company}, {industry}, {industryCode}, {today})")
                self.conn.commit()
                print('')              

    def read_naver(self, code, company, pages_to_fetch):
        return None
#     def read_naver(self, code, company, pages_to_fetch):
#         """네이버에서 주식 시세를 읽어서 데이터프레임으로 반환"""
#         try:
#             url = f"http://finance.naver.com/item/sise_day.nhn?code={code}"
#             html = BeautifulSoup(requests.get(url,
#                 headers={'User-agent': 'Mozilla/5.0'}).text, "lxml")
#             pgrr = html.find("td", class_="pgRR")
#             if pgrr is None:
#                 return None
#             s = str(pgrr.a["href"]).split('=')
#             lastpage = s[-1] 
#             krx = pd.DataFrame()
#             pages = min(int(lastpage), pages_to_fetch)
#             for page in range(1, pages + 1):
#                 pg_url = '{}&page={}'.format(url, page)
#                 krx = krx.append(pd.read_html(requests.get(pg_url,
#                     headers={'User-agent': 'Mozilla/5.0'}).text)[0])                                          
#                 tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
#                 print('[{}] {} ({}) : {:04d}/{:04d} pages are downloading...'.
#                     format(tmnow, company, code, page, pages), end="\r")
#             krx = krx.rename(columns={'날짜':'date','종가':'close','전일비':'diff'
#                 ,'시가':'open','고가':'high','저가':'low','거래량':'volume'})
#             krx['date'] = krx['date'].replace('.', '-')
#             krx = krx.dropna()
#             krx[['close', 'diff', 'open', 'high', 'low', 'volume']] = krx[['close',
#                 'diff', 'open', 'high', 'low', 'volume']].astype(int)
#             krx = krx[['date', 'open', 'high', 'low', 'close', 'diff', 'volume']]
#             krx = krx.reset_index(drop=True)
#             df = krx.sort_values(by='date', ascending=False)

#         except Exception as e:
#             print('Exception occured :', str(e))
#             return None
#         return df

    def months_ago(self, dt, pages_to_fetch):
        if dt.month == 1:
            dt = dt.replace(month=12)
            return dt
        return dt.replace(month=dt.month - pages_to_fetch )


    def read_yahoo_finance(self, code, company, pages_to_fetch):
        """야후 파이낸스에서 주식 시세를 가져옴(데이터플레임)"""
        try:      
#             today = datetime.today() # .strftime('%Y-%m-%d')
            now = datetime.now()
            months = math.ceil( (pages_to_fetch * 10) / (262 / 12) )
#             print(months)
            start_date = now - relativedelta(months=months)
#             print (start_date.strftime('%Y-%m-%d'))
#             start_date = self.months_ago(today, pages_to_fetch).strftime('%Y-%m-%d')

            stock = fdr.DataReader(code, start_date.strftime('%Y-%m-%d')) # '2018-01-01'
            days_ago = 10 * pages_to_fetch
            stock = stock[-(days_ago+1):]
            stock['diff'] = abs( stock['Close'] - stock['Close'].shift(1))
            stock = stock.reset_index()[-days_ago:].sort_values(by='Date', ascending=False)
            stock = stock.rename(columns={'Date':'date','Close':'close','diff':'diff'
                ,'Open':'open','High':'high','Low':'low','Volume':'volume'})
            stock = stock[['date','open','high','low','close','diff','volume']]
            df = stock.reset_index(drop=True)
            df.dropna(inplace=True)
        except Exception as e:
            print('Exception occured :', str(e))
            return None
        return df
    
    def replace_into_db(self, df, num, code, company):
        """네이버에서 읽어온 주식 시세를 DB에 REPLACE"""
        with self.conn.cursor() as curs:
            for r in df.itertuples():
                sql = f"REPLACE INTO daily_price VALUES ('{code}', "\
                    f"'{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, "\
                    f"{r.diff}, {r.volume})"
                curs.execute(sql)
            self.conn.commit()
            print('[{}] #{:04d} {} ({}) : {} rows > REPLACE INTO daily_'\
                'price [OK]'.format(datetime.now().strftime('%Y-%m-%d'\
                ' %H:%M'), num+1, company, code, len(df)))

    def update_daily_price(self, pages_to_fetch):
        """KRX 상장법인의 주식 시세를 네이버로부터 읽어서 DB에 업데이트"""  
        for idx, code in enumerate(self.codes):
            if code.isdigit() == True:
                df = self.read_naver(code, self.codes[code], pages_to_fetch)
            else:
                df = self.read_yahoo_finance(code, self.codes[code], pages_to_fetch)
            if df is None:
                continue
            self.replace_into_db(df, idx, code, self.codes[code])            

    def execute_daily(self):
        """실행 즉시 및 매일 오후 다섯시에 daily_price 테이블 업데이트"""
        self.update_comp_info()
        
        try:
            with open('config.json', 'r') as in_file:
                config = json.load(in_file)
                pages_to_fetch = config['pages_to_fetch']
        except FileNotFoundError:
            with open('config.json', 'w') as out_file:
                pages_to_fetch = 100 
                config = {'pages_to_fetch': 1}
                json.dump(config, out_file)
        self.update_daily_price(pages_to_fetch)

        tmnow = datetime.now()
        lastday = calendar.monthrange(tmnow.year, tmnow.month)[1]
        if tmnow.month == 12 and tmnow.day == lastday:
            tmnext = tmnow.replace(year=tmnow.year+1, month=1, day=1,
                hour=17, minute=0, second=0)
        elif tmnow.day == lastday:
            tmnext = tmnow.replace(month=tmnow.month+1, day=1, hour=17,
                minute=0, second=0)
        else:
            tmnext = tmnow.replace(day=tmnow.day+1, hour=17, minute=0,
                second=0)   
        tmdiff = tmnext - tmnow
        secs = tmdiff.seconds
        t = Timer(secs, self.execute_daily)
        print("Waiting for next update ({}) ... ".format(tmnext.strftime
            ('%Y-%m-%d %H:%M')))
        t.start()

if __name__ == '__main__':
    dbu = DBUpdater()
    dbu.execute_daily()
