import os
from flask import Flask, render_template, jsonify, json, flash, redirect, request, session, abort
import bursData
import plotly
import plotly.graph_objs as go
import json
# import talib
import pandas as pd
from datetime import datetime
import jdatetime
from tinydb import TinyDB, Query
import requests
import time

app = Flask(__name__)

@app.route("/")
def home_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        market=bursData.market_pd()
        return render_template("index.html",market=market)

@app.route("/filter")
def filter_bourse():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("filter.html")

@app.route("/smart_filter")
def smart_filter():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        clientall = pd.merge(bursData.client_all_pd(), bursData.market_pd(), on='id')
        clientall['sell_ho_tot']=(100*clientall['Sell_N_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        clientall['buy_ho_tot']=(100*clientall['Buy_N_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        clientall['sell_ha_tot']=(100*clientall['Sell_I_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        clientall['buy_ha_tot']=(100*clientall['Buy_I_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        time = jdatetime.datetime.now().strftime("%H:%M:%S")
        clientall = clientall[~clientall['group_id'].apply(int).isin([68,69,59])]
        clientall=clientall[[not any(map(str.isdigit, i)) for i in clientall['symbol']]]
        market=clientall[(clientall['buy_ha_tot'].apply(float) > 70) & (clientall['sell_ho_tot'].apply(float) > 30)]
        for _,id in market['id'].iteritems():
            result = pd.merge(bursData.general_dayinfo_pd(id), bursData.saf_pd(id), left_index=True, right_index=True)
            market.loc[market['id'] == id, 'buy_volume'] = result['buy_volume'][0]
            try:
                if int(result['buy_price'][0]) == int(result['max_traded_price'][0]) and int(result['buy_volume'][0]) >= 0.5*int(market.loc[market['id'] == id]['base_volume']) :
                    market.loc[market['id'] == id, 'saf'] = True
            except:
                pass
            try:
                market.loc[market['id'] == id, 'volume_mounth'] = int(bursData.history_pd(int(id),30)['volume'].mean())
            except:
                market.loc[market['id'] == id, 'volume_mounth'] = 0

        return render_template("smart_filter.html",market=clientall,smartmarket=market,time=time)


@app.route("/fipiran")
def fipiran():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        fipiran=bursData.fipiran()
        return render_template("fipiran.html",market=fipiran)


@app.route('/alarm')
def alarm():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        clientall = pd.merge(bursData.client_all_pd(), bursData.market_pd(), on='id')
        clientall['sell_ho_tot']=(100*clientall['Sell_N_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        clientall['buy_ho_tot']=(100*clientall['Buy_N_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        clientall['sell_ha_tot']=(100*clientall['Sell_I_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        clientall['buy_ha_tot']=(100*clientall['Buy_I_Volume'].apply(int)/clientall['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        clientall = clientall[~clientall['group_id'].apply(int).isin([68,69,59])]
        clientall=clientall[[not any(map(str.isdigit, i)) for i in clientall['symbol']]]
        market=clientall[(clientall['buy_ha_tot'].apply(float) > 70) & (clientall['sell_ho_tot'].apply(float) > 30)]
        market=market[[not any(map(str.isdigit, i)) for i in market['symbol']]]
        for _,id in market['id'].iteritems():
            try:
                market.loc[market['id'] == id, 'volume_mounth'] = int(bursData.history_pd(int(id),30)['volume'].mean())
            except:
                market.loc[market['id'] == id, 'volume_mounth'] = 0
            # hist=bursData.history_pd(int(id),30)
            # hist['date']=pd.to_datetime(hist['date']).apply(lambda x: jdatetime.datetime.fromgregorian(datetime=x).strftime('%Y-%m-%d'))
            # market.loc[market['id'] == id, 'till'] = hist['date'].iloc[29]
            # market.loc[market['id'] == id, 'volume_mounth'] = hist['volume'].head(30).sum()/30
            # market.loc[market['id'] == id, 'volume_mounth_today'] = (hist['volume'].head(29).sum()+int(market[market['id'] == id]['volume']))/30
            
        return render_template("alarm.html",market=market)
        # return jsonify(market.to_json())

@app.route('/stock/<int:id>')
def stosk_view(id):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        market=bursData.market_pd()
        symbol=market.loc[market['id'] == str(id)]['symbol'].values[0]
        name=market.loc[market['id'] == str(id)]['name'].values[0]
        groupid=market.loc[market['id'] == str(id)]['group_id'].values[0]
        group_list=market.loc[market['group_id'] == groupid ]
        day_price_list=bursData.dayprice_pd(int(id))
        general=bursData.general_dayinfo_pd(id)
        saf=bursData.saf_pd(id)

        Candlestick = go.Candlestick(x=day_price_list['time'], open=day_price_list['open_price'], high=day_price_list['high_price'], low=day_price_list['low_price'], close=day_price_list['close_price'])
        data=[Candlestick]
        shapes = {"shapes": []}
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        shapesJSON = json.dumps(shapes, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("stock.html", plot=graphJSON, layout=shapesJSON, id=id,name=name ,symbol=symbol,group_list=group_list,saf=saf,general=general,day_price_list=day_price_list)

@app.route('/history/<int:id>')
def history_view(id):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        hist=bursData.history_pd(int(id))
        market=bursData.market_pd()
        symbol=market.loc[market['id'] == str(id)]['symbol'].values[0]
        name=market.loc[market['id'] == str(id)]['name'].values[0]
        
        hist['date']=pd.to_datetime(hist['date']).apply(lambda x: jdatetime.datetime.fromgregorian(datetime=x).strftime('%Y-%m-%d'))

        Candlestick = go.Candlestick(x=hist['date'], open=hist['first_price'], high=hist['max_price'], low=hist['min_price'], close=hist['close_price'])
        data=[Candlestick]
        shapes = {"shapes": []}
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        shapesJSON = json.dumps(shapes, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("history.html", plot=graphJSON, layout=shapesJSON, hist=hist, symbol=symbol, name=name, id=int(id))

@app.route('/client_history/<int:id>')
def client_history_view(id):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        hist = pd.merge(bursData.client_history_pd(int(id)), bursData.history_pd(int(id)), on='date')
        market=bursData.market_pd()
        symbol=market.loc[market['id'] == str(id)]['symbol'].values[0]
        name=market.loc[market['id'] == str(id)]['name'].values[0]
        hist['date']=pd.to_datetime(hist['date']).apply(lambda x: jdatetime.datetime.fromgregorian(datetime=x).strftime('%Y-%m-%d'))
        
        data = [go.Bar(name='حجم خرید حقوقی', x=hist['date'], y=hist['hoghughi_buy_volume']),
                go.Bar(name='حجم فروش حقوقی', x=hist['date'], y=hist['hoghughi_sell_volume']),
                go.Bar(name='حجم خرید حقیقی', x=hist['date'], y=hist['haghighi_buy_volume']),
                go.Bar(name='حجم فروش حقیقی', x=hist['date'], y=hist['haghighi_sell_volume'])]
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        hist['sell_ho_tot']=(100*hist['hoghughi_sell_volume'].apply(int)/hist['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))
        hist['buy_ho_tot']=(100*hist['hoghughi_buy_volume'].apply(int)/hist['volume'].apply(int)).apply(lambda x: '{:.2f}'.format(x))

        return render_template("client_history.html", plot=graphJSON, hist=hist, symbol=symbol, name=name, id=int(id))

@app.route('/update')
def update():
    jdatetime.set_locale('fa_IR')
    date = jdatetime.datetime.now().strftime("%a, %d %b %Y")
    time = jdatetime.datetime.now().strftime("%H:%M:%S")
    return jsonify({'time': time,'date': date})

@app.route('/update_value')
def update_value():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if(requests.get('http://www.tsetmc.com/tsev2/data/ClientTypeAll.aspx').status_code == 200):
            db = TinyDB('./values_IN.json')
            date = jdatetime.datetime.now().strftime("%Y-%m-%d")
            time = jdatetime.datetime.now().strftime("%H:%M:%S")
            clientall = pd.merge(bursData.client_all_pd(), bursData.market_pd(), on='id')
            tot_Buy_I_Value = (clientall['Buy_I_Volume'].apply(int)*clientall['last_price'].apply(int)).sum()/1000000000000
            tot_Buy_N_Value = (clientall['Buy_N_Volume'].apply(int)*clientall['last_price'].apply(int)).sum()/1000000000000
            tot_Sell_I_Value = (clientall['Sell_I_Volume'].apply(int)*clientall['last_price'].apply(int)).sum()/1000000000000
            tot_Sell_N_Value = (clientall['Sell_N_Volume'].apply(int)*clientall['last_price'].apply(int)).sum()/1000000000000
            if(jdatetime.date.today().weekday() < 5):
                db.upsert({'date': date, 'time': time, 'tot_Buy_I_Value':tot_Buy_I_Value, 'tot_Buy_N_Value':tot_Buy_N_Value, 'tot_Sell_I_Value':tot_Sell_I_Value, 'tot_Sell_N_Value':tot_Sell_N_Value}, Query().date == date)
        return render_template("values_IN.html", values_IN=json.loads(json.dumps(db.all())))

@app.route('/login', methods=['POST'])
def login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('پسورد اشتباه میباشد')
    return redirect(request.referrer)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return login()

@app.route("/debug")
def debug():
    return 0/0

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=port, debug=True)