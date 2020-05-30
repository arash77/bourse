import pandas as pd
import numpy as np
import bursApi
from datetime import datetime
import threading

pd.options.mode.chained_assignment = None

def market_pd():
    market = None
    while not market:
        try:
            market=bursApi.market()
        except:
            pass
    market_np=np.empty((0,22))
    for i in market:
        market_np=np.concatenate((market_np,np.array([list(market[i].values())])))
    market_pd=pd.DataFrame(market_np,columns=list(market[i].keys()))
    return market_pd

def CCI(close, high, low, n, constant): 
     TP = (high + low + close) / 3 
     CCI = pd.Series((TP - TP.rolling(n).mean()) / (constant * TP.rolling(n).std()), name = 'CCI_' + str(n)) 
     return CCI

def all_data(id):
    all_data={}
    all_data['dayinfo']=bursApi.get_dayinfo(id)
    all_data['dayprice']=bursApi.get_dayprice(id)
    all_data['clienttype_history']=bursApi.get_clienttype_history(id)
    return all_data
    
def saf_pd(id):
    day = None
    while not day:
        try:
            day=bursApi.get_dayinfo(int(id))
        except:
            pass
    saf_np=np.empty((0,6))
    for i in range(1,4):
        try:
            saf_np=np.concatenate((saf_np,np.array([list(day[i].values())])))
        except:
            pass
    saf_pd=pd.DataFrame(saf_np,columns=list(day[1].keys()))
    return saf_pd  

def general_dayinfo_pd(id):
    general = None
    while not general:
        try:
            general=bursApi.get_day_general_info(int(id))
        except:
            pass
    general_dayinfo_np=np.empty((0,13))
    general_dayinfo_np=np.concatenate((general_dayinfo_np,np.array([list(general.values())])))
    general_dayinfo_pd=pd.DataFrame(general_dayinfo_np,columns=list(general.keys()))
    return general_dayinfo_pd

def dayprice_pd(id):
    day = None
    i=0
    while not day:
        try:
            day=bursApi.get_dayprice(int(id))
        except:
            i+=1
            if i==3:
                break

    dayprice_np=np.empty((0,6))
    for i in day:
        dayprice_np=np.concatenate((dayprice_np,np.array([list(i.values())])))
    dayprice_np[:,1:]=dayprice_np[:,1:].astype(int)
    dayprice_pd=pd.DataFrame(dayprice_np,columns=list(day[0].keys()))
    now=datetime.now()
    for i in range(len(dayprice_pd.time)):
        s=dayprice_pd.time[i].split(':')
        dayprice_pd.time[i]=datetime(now.year,now.month,now.day,int(s[0]),int(s[1]))
    dayprice_pd.iloc[:,1:]= dayprice_pd.iloc[:,1:].astype(np.int64)
    return dayprice_pd

def dayinfo_pd(id):
    day = None
    while not day:
        try:
            day=bursApi.get_dayinfo(int(id))
        except:
            pass
    try:
        dayinfo_np=np.empty((0,13))
        dayinfo_np=np.concatenate((dayinfo_np,np.array([list(day[0].values())])))
    except:
        dayinfo_np=np.empty((0,21))
        dayinfo_np=np.concatenate((dayinfo_np,np.array([list(day[0].values())])))
    dayinfo_pd=pd.DataFrame(dayinfo_np,columns=list(day[0].keys()))
    return dayinfo_pd

def history_pd(id,num=99999):
    hist=bursApi.get_history(int(id),int(num))
    history_np=np.empty((0,10))
    for i in hist:
        history_np=np.concatenate((history_np,np.array([list(i.values())])))
    history_np[:,1:]=history_np[:,1:].astype(float)
    history_pd=pd.DataFrame(history_np,columns=list(hist[1].keys()))
    history_pd.iloc[:,1:]= history_pd.iloc[:,1:].astype(float)
    history_pd.iloc[:,1:]= history_pd.iloc[:,1:].astype(np.int64)
    history_pd=history_pd.iloc[::-1]
    # TP = (history_pd['max_price'] + history_pd['min_price'] + history_pd['close_price']) / 3 
    # n=20
    # constant=0.015
    # history_pd['cci20'] = pd.Series((TP - TP.rolling(n).mean()) / (constant * TP.rolling(n).std()), name = 'CCI_' + str(n)) 
    history_pd=history_pd.iloc[::-1]
    return history_pd

def client_history_pd(id):
    client_hist = None
    while not client_hist:
        try:
            client_hist=bursApi.get_clienttype_history(int(id))
        except:
            pass
    client_history_np=np.empty((0,13))
    for i in client_hist:
            client_history_np=np.concatenate((client_history_np,np.array([list(i.values())])))
    client_history_pd=pd.DataFrame(client_history_np,columns=list(client_hist[0].keys()))
    return client_history_pd


def client_all_pd():
    client_all = None
    i=0
    while not client_all:
        try:
            client_all=bursApi.get_clienttype_all()
        except:
            i+=1
            if i==3:
                break
    client_all_np=np.empty((0,9))
    for i in client_all:
            client_all_np=np.concatenate((client_all_np,np.array([list(i.values())])))
    client_all_pd=pd.DataFrame(client_all_np,columns=list(client_all[0].keys()))
    return client_all_pd

def fipiran():
    fipiran = pd.read_html('http://www.fipiran.com/Market/LupBourse',header=0)[0]
    fipiran.columns = ['symbol', 'price', 'change', 'close_price', 'change_2', 'count', 'volume', 'value', 'EPS', 'PE', 'fund', 'current_ratio', 'debt_ratio', 'net_profit', 'ROA', 'ROE']
    fipiran=fipiran.replace(np.nan,'',regex=True)
    fipiran=fipiran.replace('M','',regex=True)
    fipiran=fipiran.replace('k','',regex=True)
    fipiran=fipiran.replace(',','',regex=True)
    return fipiran


# def saving_data():
#     print("starting to update")
#     market = bursData.market_pd()
#     market = market[~market['group_id'].apply(int).isin([68,69,59])]
#     market = market[market['count'].apply(int)>0]
#     market = market[[not any(map(str.isdigit, i)) for i in market['symbol']]]
#     market.to_csv("stock_data/market_pd.csv")
#     bursData.client_all_pd().to_csv("stock_data/client_all_pd.csv")
#     bursData.fipiran().to_csv("stock_data/fipiran.csv")
#     for _,id in market['id'].iteritems():
#         bursData.saf_pd(id).to_csv("stock_data/saf_pd_{}.csv".format(id))
#         bursData.general_dayinfo_pd(id).to_csv("stock_data/general_dayinfo_pd_{}.csv".format(id))
#         bursData.dayprice_pd(id).to_csv("stock_data/dayprice_pd_{}.csv".format(id))
#         bursData.dayinfo_pd(id).to_csv("stock_data/dayinfo_pd_{}.csv".format(id))
#         bursData.history_pd(id).to_csv("stock_data/history_pd_{}.csv".format(id))
#         bursData.client_history_pd(id).to_csv("stock_data/client_history_pd_{}.csv".format(id))
#     print("done updateing")
#     threading.Timer(3600,saving_data).start()
# saving_data()