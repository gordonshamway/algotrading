import quandl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy import where
from datetime import datetime
from dateutil import relativedelta

#'CONST'
quandl.ApiConfig.api_key = "s2wz9dpCym92wjd3cwb8"

# Linus Ursprung
##def weekly_avg_adj_close_percent(symbol,timerange='all',plot= False):
symbol='KO'
#Daten einlesen
mydata1 = quandl.get("WIKI/{}".format(symbol))

#Datentyp umwandeln
mydata1['date_timestamp'] = pd.to_datetime(mydata1.index)
print(mydata1)

#Zugriff auf Daten
d = mydata1['2017-09-29':'2017-10-09'] #ok hier kann ich meine start und enddate werte eintragen
#mydata[startdate:enddate]

#function um meine berechnungen durchzuführen:
def calc_profit(df):
    start = df['Close'].iloc[0]
    end = df['Close'].iloc[-1]
    profit = end-start
    profit_percent = profit/start
    return start, end, profit, profit_percent

def calcMaxRiseDrop(df):
    maxDrop = np.nanmin((df.Close - df.Close.shift(1)) / df.Close.iloc[0])
    maxRise = np.nanmax((df.Close - df.Close.shift(1)) / df.Close.iloc[0])
    return maxDrop, maxRise

def distance_calcs(df):
    startprice, endprice, profit, profit_percent = calc_profit(df)
    maxDrop, maxRise = calcMaxRiseDrop(df)
    indexinfo = df.index.tolist()
    startdate = indexinfo[0]
    enddate = indexinfo[-1]
    return startdate, startprice, enddate, endprice, profit, profit_percent, maxRise, maxDrop

result = distance_calcs(d)
print(result)
#Main
#weekly_avg_adj_close_percent('KO')
