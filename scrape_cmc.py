import time
import requests
import random
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, timedelta

def allsundays(year):
    d = date(year, 1, 1)
    d += timedelta(days = 6 - d.weekday())
    while d.year == year:
        yield d
        d += timedelta(days = 7)


def create_df(timestamps):
    df = pd.DataFrame()
    for t in timestamps:
        print('fetching data from', t)
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
        print('job done!')
    df = df.replace('\n','', regex=True)
    df.columns = ['#', 'Name', 'Symbol', 'MktCap', 'Price', 'Circulating Supply', 'Volume (24h)','% 1h', '% 24h', '% 7d', 'delete', 'Date']
    df.MktCap = df.MktCap.str.replace(',', '').str.replace('$', '')
    df = df.drop('delete', axis=1)
    df = df.set_index('Date', inplace=True)
    return df

timestamps = []
for d in allsundays(2018):
    timestamps.append(d.strftime("%Y, %m, %d").replace(',','').replace(' ', ''))
df = create_df(timestamps)