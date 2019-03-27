import pandas as pd
import numpy as np
import datetime
from requests import Session
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def get_cmc():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
      'start': '1',
      'limit': '10',
      'convert': 'USD',
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': '09733d82-ec67-40de-8f0a-dedf02b1450d',
    }

    session = Session()
    session.headers.update(headers)
    mktcap = []
    coins = []
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)['data']
        for n in range(9):
            coins.append(data[n]['symbol'])
            mktcap.append(data[n]['quote']['USD']['market_cap'])
        df = pd.DataFrame(mktcap, coins)
        return coins, df, mktcap
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
def daily_price_historical(symbol, comparison_symbol, all_data=True, limit=1, aggregate=1, exchange=''):
    url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&limit={}&aggregate={}'\
            .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate)
    if exchange:
        url += '&e={}'.format(exchange)
    if all_data:
        url += '&allData=true'
    page = requests.get(url)
    data = page.json()['Data']
    df = pd.DataFrame(data)
    df['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
    return df

def get_daily_data(base, pairs):
    df = pd.DataFrame(columns=pairs)
    for p in pairs:
        temp_df = daily_price_historical(p, base)
        temp_df = temp_df.set_index(temp_df.timestamp)
        df[p] = temp_df.close
        print(p, 'successfully imported')
    return df.dropna()

def allocation(mktcaps, pairs):
    pct = []
    s = sum(mktcaps)
    for c in mktcaps:
        pct.append(100/s*c)
    return pd.DataFrame(pct, pairs)



base = 'USD'

pairs, comp_df, mktcap = get_cmc()
daily_df = get_daily_data(base, pairs)
alloc = allocation(mktcap, pairs)

print(alloc)