import bursData
import os
import time
start_time = time.time()
if not os.path.exists('stock_data'):
    os.makedirs('stock_data')

print("starting!")
market = bursData.market_pd()
market = market[~market['group_id'].apply(int).isin([68,69,59])]
market = market[market['count'].apply(int)>0]
market = market[[not any(map(str.isdigit, i)) for i in market['symbol']]]
market.to_csv("stock_data/market_pd.csv")
bursData.client_all_pd().to_csv("stock_data/client_all_pd.csv")
bursData.fipiran().to_csv("stock_data/fipiran.csv")
for _,id in market['id'].iteritems():
    print(id)
    bursData.saf_pd(id).to_csv("stock_data/saf_pd_{}.csv".format(id))
    bursData.general_dayinfo_pd(id).to_csv("stock_data/general_dayinfo_pd_{}.csv".format(id))
    bursData.dayprice_pd(id).to_csv("stock_data/dayprice_pd_{}.csv".format(id))
    bursData.dayinfo_pd(id).to_csv("stock_data/dayinfo_pd_{}.csv".format(id))
    bursData.history_pd(id).to_csv("stock_data/history_pd_{}.csv".format(id))
    bursData.client_history_pd(id).to_csv("stock_data/client_history_pd_{}.csv".format(id))
    print("--- {:.2f} seconds ---".format(time.time() - start_time))
print("done")