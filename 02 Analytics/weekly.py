import quandl
import matplotlib.pyplot as plt
import pandas as pd
from numpy import where
from datetime import datetime
from dateutil import relativedelta

#'CONST'
quandl.ApiConfig.api_key = "s2wz9dpCym92wjd3cwb8"

# Linus Ursprung
def weekly_avg_adj_close_percent(symbol,timerange='all',plot= False):
     #Daten einlesen
     mydata1 = quandl.get("WIKI/{}".format(symbol))

     #Datentyp umwandeln
     mydata1['date_timestamp'] = pd.to_datetime(mydata1.index)
     mydata1['date_datetime']= mydata1['date_timestamp'].dt.date
     mydata1['wochentag']=mydata1['date_timestamp'].dt.dayofweek

     #prozentuale aenderung ermitteln
     mydata1['Adj. Close percent'] = mydata1['Adj. Close'].pct_change()

     #filtern
     mydata1_filter = mydata1[['wochentag','Adj. Close percent']]
     df_weekly_perc = mydata1_filter.groupby('wochentag').agg('mean')
     if plot:
         df_weekly_perc.plot.bar(title=symbol)
     return df_weekly_perc

def get_dateinfo_columns(df, datecolumnname):
    df[datecolumnname + '_year'] = df[datecolumnname].dt.year
    df[datecolumnname + '_quarter'] = df[datecolumnname].dt.quarter
    df[datecolumnname + '_month'] = df[datecolumnname].dt.month
    df[datecolumnname + '_week'] = df[datecolumnname].dt.week
    df[datecolumnname + '_dayofweek'] = df[datecolumnname].dt.dayofweek #1 Monday?
    df[datecolumnname + '_day'] = df[datecolumnname].dt.day
    return df

def build_fixed_time_dataset(md, enum):
    ''' build dataframe of constant time differencet 1 week, 1 month, 1 quarter, 1 year, etc
        distance is always 1
    '''
    # numbers of a.dict will be ignored here, just a copy
    a = {
        'day': 1,
        'week': 7,
        'month': 30,
        'quarter': 90,
        'year': 365
    }

    # calc min and max
    minDate = min(md['startdate'])
    maxDate = max(md['startdate'])

    # calculate the number of enums inbetween the two dates
    noYears = pd.period_range(minDate, maxDate, freq='A')  # für jahre
    noQuarters = pd.period_range(minDate, maxDate, freq='Q')  # für quartale aber das date wird dann grob
    noMonths = pd.period_range(minDate, maxDate, freq='M')  # für monate
    noWeeks = pd.period_range(minDate, maxDate, freq='W-MON')  # für wochenanfang Montag z.B. 1947
    noDays = pd.period_range(minDate, maxDate, freq='D')  # für Tage

    if enum=='year':
        shiftRange = noYears
    elif enum =='quarter':
        shiftRange = noQuarters
    elif enum == 'month':
        shiftRange = noMonths
    elif enum == 'week':
        shiftRange = noWeeks
    elif enum == 'day':
        shiftRange = noDays
    else:
        pass

    # TODO ich muss noch überlegen wie ich mehrere enums shifte und dann zusammenbaue

    anfangszeiten = shiftRange.start_time
    endzeiten = shiftRange.end_time
    frames = {'startdate': anfangszeiten, 'enddate': endzeiten}
    res = pd.DataFrame(frames)
    res['name'] = enum
    res.reset_index(drop=True)
    return res


def build_fixed_distance_dataset(md, enum):
    ''' build dataframe of constant 5 business days -> week distance (7 days) '''
    #enum dict for valid values
    a = {
        'day': 1,
        'week': 7,
        'month': 30,
        'quarter': 90,
        'year': 365
    }

    # calc min and max
    minDate = min(md['startdate'])
    maxDate = max(md['startdate'])

    # calculate the number of enums inbetween the two dates
    noYears = len(pd.period_range(minDate, maxDate, freq='A'))  # für jahre
    noQuarters = len(pd.period_range(minDate, maxDate, freq='Q'))  # für quartale aber das date wird dann grob
    noMonths = len(pd.period_range(minDate, maxDate, freq='M'))  # für monate
    noWeeks = len(pd.period_range(minDate, maxDate, freq='W-MON'))  # für wochenanfang Montag z.B. 1947
    noDays = len(pd.period_range(minDate, maxDate, freq='D'))  # für Tage

    if enum=='year':
        shiftRange = noYears
    elif enum =='quarter':
        shiftRange = noQuarters
    elif enum == 'month':
        shiftRange = noMonths
    elif enum == 'week':
        shiftRange = noWeeks
    elif enum == 'day':
        shiftRange = noDays
    else:
        pass

    # combine the iterated datasets to a new big one
    #print('there are {} amount of same distance {}s'.format(shiftRange, enum))
    #print(len(md.index))
    appendlist = []
    for i in range(shiftRange): #amount of weeks, months, quarters
        df = md.copy()
        df['enddate'] = md['startdate'] + pd.DateOffset( a[enum] * (i+1) ) #shift daily
        df['name'] = 'added {} {}(s)'.format(i+1,enum)
        appendlist.append(df)
    appended_dfs = pd.concat(appendlist, axis=0)
    return appended_dfs


def lookup_prices(dataframe_with_start_and_enddate, lookupdataframe):
    ''' performs a lookup to get start and end prices for the time '''
    df1 = lookupdataframe.set_index('startdate')['Adj. Close'].to_dict()
    dataframe_with_start_and_enddate['startprice'] = dataframe_with_start_and_enddate['startdate'].map(df1)
    dataframe_with_start_and_enddate['endprice'] = dataframe_with_start_and_enddate['enddate'].map(df1)
    dataframe_with_start_and_enddate.dropna(how='any')
    return dataframe_with_start_and_enddate


def calc_diffs(df):
    ''' calculates the profit or loss in abolut and percentages and flags winner or loser'''
    df['abs_diff'] = df['endprice'] - df['startprice']
    df['perct_chng'] = df['abs_diff'] / df['startprice']
    df.loc[df['abs_diff'] > 0, 'flag'] = 'winner'
    df.loc[df['abs_diff'] < 0, 'flag'] = 'looser'
    df = df.dropna(how='any')
    return df

def anaylze_seasonality(df, aggregating_column):
    ''' aggregates the number of winners and loosers and their statistics per name '''
    workingdf = df[['name', aggregating_column, 'flag', 'abs_diff', 'perct_chng']]
    workingdf['winner'] = where(workingdf['flag']=='winner', 1, 0)
    workingdf['looser'] = where(workingdf['flag'] == 'looser', 1, 0)
    last = workingdf.groupby(['name', aggregating_column], as_index=False).agg({'abs_diff': ['sum','mean', 'std'], 'perct_chng': ['sum','mean', 'std'], 'winner': 'sum', 'looser': 'sum'})#.agg({
    last['winrate'] = last['winner'] / (last['winner'] + last['looser'])
    last = last.sort_values(by=['winrate'],ascending=False)
    return last

###### main ####
dataset = quandl.get("WIKI/{}".format('AAPL'))
dataset['startdate'] = pd.to_datetime(dataset.index)
dataset.reset_index()

##### Workflow to calculate fixed time distance i.e. week = 7 day distance, for everyday there is
## Preparation - just makeup a lookup dataset
#df1 = dataset[['startdate', 'Adj. Close']]

## build working dataset
#weekly_distance = build_fixed_distance_dataset(dataset,'quarter')
#weekly_distance = get_dateinfo_columns(weekly_distance, 'startdate')
#weekly_distance = get_dateinfo_columns(weekly_distance, 'enddate')

## make other calculations
#prepared = lookup_prices(weekly_distance, df1)
#with_diffs = calc_diffs(prepared)
#print(with_diffs.to_string()) # just to see more for checking

##### Workflow to have fixed time definition distances
test = build_fixed_time_dataset(dataset, 'month')
test2 = get_dateinfo_columns(test, 'startdate')
test2 = get_dateinfo_columns(test2, 'enddate')
test_with_prices = lookup_prices(test2, dataset)
test_with_pricesdiff = calc_diffs(test_with_prices)
final = anaylze_seasonality(test_with_pricesdiff, 'startdate_week')
final_filter = final[final['looser','sum']>5]
final_filter.sort_index().winrate.plot()

print(final.to_string())
