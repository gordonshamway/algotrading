import quandl
import pandas as pd

mydata1 = quandl.get("WIKI/AAPL")
mydata1.to_pickle('C:/Users/Deike/algotrading/git/03 machine learning/data/input/aapl.p')

