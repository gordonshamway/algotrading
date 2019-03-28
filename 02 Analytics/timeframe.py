import pandas as pd
import quandl

quandl.ApiConfig.api_key = "s2wz9dpCym92wjd3cwb8"
'''
UX Flow:
    1. Pick symbol to analyse
    2. Pick timeframe to analyse (yearly)
    3. Maybe pick timeperiod to analyse (20 years)
    4. Pick start and enddate
    5. Now comes the todo!
TODO: We want to pick a date based out of a complete date dimension, the picked start and enddate should for every
find the next trading day for the stock
    For every year make the finding.
'''

# TODO: The whole script is really not needed anymore i think, maybe i can annotate the distance in the Combinations Table
# to have this feature

# 1. I don´t need this anymore
def create_date_table(start='2000-01-01', end='2050-12-31'):
    df = pd.DataFrame({"Date": pd.date_range(start, end)})
    df["Day"] = df.Date.dt.weekday_name
    df["Week"] = df.Date.dt.weekofyear
    df["Month"] = df.Date.dt.month
    df["Quarter"] = df.Date.dt.quarter
    df["Year"] = df.Date.dt.year
    df.set_index("Date", inplace=True)
    return df

def getdata():
    symbol = 'KO'
    mydata1 = quandl.get("WIKI/{}".format(symbol))
    mydata1['date_timestamp'] = pd.to_datetime(mydata1.index)
    return mydata1


def pickCorrectDate(someDate, securitydf):
    a = someDate
    i=1
    while a not in securitydf.index:
        a = someDate + pd.DateOffset(days=i)
        i +=1
    return a


def yearlyDates(someDate, timeframe, df):
    validDates = []
    for x in range(timeframe):
        a = someDate -pd.DateOffset(years=x)
        res = pickCorrectDate(a, df)
        validDates.append(res)
    return validDates

#### Main ##################################
d = getdata() #just to get data
# the guy in the frontend chooses some start end enddate
entryStartDate = pd.to_datetime('2018-03-16')
entryEndDate = pd.to_datetime('2018-03-17')
exactStartDates = yearlyDates(entryStartDate, 10, d)
exactEndDates = yearlyDates(entryEndDate, 10, d)

print(exactStartDates)


