import time
import pandas as pd
import quandl
import datetime

quandl.ApiConfig.api_key = "s2wz9dpCym92wjd3cwb8"
# Here all the functions should be located which transforms the backend data
# into new insights and loads them back into the database

#TODO: Load data from Backend into RAM

def getdata():
    symbol = 'KO'
    mydata1 = quandl.get("WIKI/{}".format(symbol))
    mydata1['date_timestamp'] = pd.to_datetime(mydata1.index)
    return mydata1

def pickCorrectDate(someDate, securitydf):
    a = someDate
    i=1
    try:
        while a not in securitydf.index:
            a = someDate + pd.DateOffset(days=i)
            i +=1
    except:
        return None
    return a

def createDateTuples(basedf, start='1990-01-01', end='2018-03-17'):
    # TODO: Create all possible Start-End-Date-Combinations to calculate, once calculated push to db
    # Get Maximum Date from the security, subtract i where i = 1..365 where the resultdate is startdate, then subtract 1
    # from maximum_date
    # always use the datepicker to get the correct tuples

    # eigentlich muss ich das nur einmal für alle Securities durchführen! ha ca. 235secs = 2,5 mins
    combinations = {}
    df = pd.DataFrame({"Date": pd.date_range(start, end)})
    for row in df.itertuples():
        startDateValue = pickCorrectDate(row[1], basedf)
        rangeDays = (pd.to_datetime(end) - startDateValue).days
        # maximum einziehen!
        if rangeDays > 365:
            rangeDays = 365
        for i in range(rangeDays): #hier kann ich klüger addieren, und zwar immer die range von enddate -startdate in tagen als range eingabe!
            entry = {}
            endDateValue = pickCorrectDate(row[1] + pd.DateOffset(days=i), basedf)
            # just to have valid dates to get quotes from
            if endDateValue and endDateValue <= end:
                entry['startDate'] = startDateValue
                entry['endDate'] = endDateValue
                try:
                    # no 1 day frames
                    if startDateValue != endDateValue:
                        combinations[startDateValue.strftime('%Y-%m-%d') + '_' + endDateValue.strftime('%Y-%m-%d')] = entry
                except KeyError:
                    pass
    return combinations

# main
t1 = time.time()
d = getdata()
max_date = d.index[-1]
#print(d.index[0])
#print(max_date)
calender = createDateTuples(d, end=max_date)
t2 = time.time()
print(t2-t1)

#print(calender.keys())
#print(calender)