import quandl
import pandas as pd
import numpy as np

#'CONST'
quandl.ApiConfig.api_key = "s2wz9dpCym92wjd3cwb8"

def get_historic_vola(symbol):

    today =
    start_date = today-365

    mydata1 = quandl.get("WIKI/{}".format(symbol), start_date="2018-01-01", end_date="2019-02-06")
    # Datentyp umwandeln
    mydata1['date_timestamp'] = pd.to_datetime(mydata1.index)
    mydata1['date_datetime'] = mydata1['date_timestamp'].dt.date
    mydata1['wochentag'] = mydata1['date_timestamp'].dt.dayofweek

    # prozentuale aenderung ermitteln
    mydata1['Adj. Close percent'] = mydata1['Adj. Close'].pct_change()
    stdabw= mydata1.loc[:, "Adj. Close percent"].std()
    vola = stdabw * np.sqrt(len(mydata1))
    print(vola)
    return vola

def get_

get_historic_vola('MO')