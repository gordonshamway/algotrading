import time
import pandas as pd
import quandl
import datetime

quandl.ApiConfig.api_key = "s2wz9dpCym92wjd3cwb8"
# Here all the functions should be located which transforms the backend data
# into new insights and loads them back into the database

# TODO: Load data from Backend into RAM
# TODO: rename to something that describes that combinations are just called once, or shall i do it incrementally?

def getdata():
    '''
    Downloads data from quandl as a base dataset to get the correct trading days.
    Takes KO as the base symbol for trading, because it trades  that long,
    could be exchanged with the SP500
    '''
    symbol = 'KO'
    mydata1 = quandl.get("WIKI/{}".format(symbol))
    mydata1['date_timestamp'] = pd.to_datetime(mydata1.index)
    return mydata1

def pickCorrectDate(someDate, securitydf):
    '''
    PURPOSE:
    Assures that when chosen a given date from the date picker in the frontend, that it will
    be translated in the next valid tradingday of a security.
    Might not need a security, once all securities have the same trading days.
    
    INPUT:
    someDate -> needs to be a correct date
    securityDF -> pandas dataframe of a stock
    
    RETURN:
    date object of the next best trading date
    '''
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
    '''
    PURPOSE:
    calculates all possible tradingday combinations of a given STOCK in a defined calendar period
    (abreviates trading days from a normal calendar period)
    Has to run once to build a reference table which can be used by other calculations
    
    INPUT:
    A base df - pandas dataframe
    valid calendar days for:
     - startdate
     - enddate
    
    RETURN:
    Saves the combinations to a database
    '''
    # TODO: push to db
    # TODO: add the range of the calendar to the dictionary
    # TODO: add the range of the tradingdays to the dictionary

    # takes roughly 235secs = 2,5 mins
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


class Combinations(base):
    '''
    defines the SQL Alchemy class so to say table to push in the calculated combinations
    '''
    # TODO: Concentrate that into a DB File which should be imported in this file and just call a method to persist into db
    __tablename__ = 'Combinations'
    id = string
    start = date
    end = date
    durationDays = int
    
    

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
