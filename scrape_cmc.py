import time
import requests
import random
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import date, timedelta

def allsundays(year):
    d = date(year, 1, 1)
    d += timedelta(days = 6 - d.weekday())
    while d.year == year:
        yield d
        d += timedelta(days = 7)
        
def everyday(year, month):
    d = date(year, month, 1)
    while d.month == month:
        yield d
        d += timedelta(days = 1)


def create_df(timestamps):
    """
    input = dates of wanted snapshots
    output = pandas dataframe with all information on coins from cmc for all the dates
    """
    df = pd.DataFrame()
    for t in timestamps:
        #print('fetching data from', t)
        time.sleep(random.uniform(1, 3))
        quote_page = 'https://coinmarketcap.com/historical/'+t
        page = requests.get(quote_page)
        second = BeautifulSoup(page.content,"lxml")
        table = second.find('div', class_ = 'table-responsive')
        while table is None:
            page = requests.get(quote_page)
            second = BeautifulSoup(page.content,"lxml")
            table = second.find('div', class_ = 'table-responsive')
        all_data = []
        for row in table.findAll('tr'):
            list_of_cells = []
            for cell in row.findAll(["th","td"]):
                text = cell.text
                list_of_cells.append(text)
            list_of_cells.append(t)
            all_data.append(list_of_cells)
        temp = pd.DataFrame(all_data[1:])
        
        df = df.append(temp, ignore_index=True)
    df = df.replace('\n','', regex=True)
    df.columns = ['#', 'Name', 'Symbol', 'MktCap', 'Price', 'Circulating Supply', 'Volume (24h)','% 1h', '% 24h', '% 7d', 'delete', 'Date']
    df.MktCap = df.MktCap.str.replace(',', '').str.replace('$', '').str.replace('?','')
    df.Price = df.Price.str.replace('$', '')
    df = df.drop(['#', 'Name', 'Circulating Supply', 'Volume (24h)','% 1h', '% 24h', '% 7d', 'delete'], axis=1)
    df.Date = pd.to_datetime(df.Date, format='%Y%m%d', errors='ignore')
    return df


def fetch_all():
    print('Starting to fetch Data from 2018')
    df = pd.DataFrame()
    for n in tqdm(range(1, 13)):
        daily_ts = []
        for d in everyday(2017, n):
            daily_ts.append(d.strftime("%Y, %m, %d").replace(',','').replace(' ', ''))
        temp = create_df(daily_ts)
        df = df.append(temp, ignore_index=True)
        #print('month nr. {} done'.format(n))
    return df

        
df = fetch_all()
print('all done, saving to csv')
df.to_csv('daily_mktcap_2017.csv', index=False)