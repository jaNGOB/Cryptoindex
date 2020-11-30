import pandas as pd
import numpy as np
from tqdm import tqdm_notebook as tqdm
from datetime import date, timedelta, datetime


def allsundays(year):
    d = datetime(year, 1, 1)
    d += timedelta(days = 6 - d.weekday())
    while d.year == year:
        yield d
        d += timedelta(days = 7)
    
def everyday(year):
    for n in range(1, 13):
        d = datetime(year, n, 1)
        while d.month == n:
            yield d
            d += timedelta(days = 1)

def clean_df(df):
    df.reset_index(inplace=True)
    df = df[df.MktCap != '']
    df = df[df.MktCap != ' ']
    df.drop(df[df.MktCap.astype(float) < 50000000].index, inplace=True)
            
    return df

def weight_df(daily, df_multi, sundays, daily_ts):
    total_list = {}
    for sun in sundays:
        for day in daily_ts:
            if sun == day:
                symbols = daily.loc[sun][:40]['Symbol'].values.tolist()
                for s in symbols:
                    mktc = df_multi.loc[s][:sun].MktCap.rolling(window=7).mean()
                    if sun not in total_list:
                        total_list[sun] = {}
                    if len(mktc) > 1:
                        total_list[sun][s] =  mktc[-1]
                
    return pd.DataFrame(total_list)


def weight_df_normal(daily, df_multi, sundays, daily_ts):
    total_list = {}
    for sun in sundays:
        for day in daily_ts:
            if sun == day:
                symbols = daily.loc[sun][:40]['Symbol'].values.tolist()
                for s in symbols:
                    mktc = df_multi.loc[s][:sun].MktCap
                    if sun not in total_list:
                        total_list[sun] = {}
                    if len(mktc) > 1:
                        total_list[sun][s] =  float(mktc[-1])
                
    return pd.DataFrame(total_list)


def allocation(mktcaps, pairs):
    pct = []
    s = sum(mktcaps)
    for c in mktcaps:
        pct.append(100/s*c/100)
    return pd.DataFrame(pct, pairs, columns=['pct'])