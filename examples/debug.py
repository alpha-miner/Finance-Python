import datetime as dt
import pandas as pd
from PyFin.Analysis.TechnicalAnalysis import SecurityTimeMovingCount


df = pd.read_csv("tmp.csv", index_col=0)

df = df.drop_duplicates((["stamp", "deviceid_c"]))

start = dt.datetime.now()
exp = SecurityTimeMovingCount("1D", "dummy")
exp.transform(df, category_field="deviceid_c")
print(dt.datetime.now() - start)
