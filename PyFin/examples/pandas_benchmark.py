# -*- coding: utf-8 -*-
u"""
Created on 2016-12-27

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
from PyFin.api import MA
from PyFin.Math.Accumulators import MovingAverage

n = 3000
m = 3000

df = pd.DataFrame(np.random.randn(n*m, 3), columns=['x', 'y', 'z'])
df['c'] = list(range(n)) * m

index = []
for i in pd.date_range(dt.datetime(1990, 1, 1), dt.datetime(1990, 1, 1) + dt.timedelta(days=m-1)):
    index += [i] * n

df.index = index

# t = MA(20, 'x') / MA(30, 'y')
#
# start = dt.datetime.now()
# res = t.transform(df, category_field='c')
# print("Finance-Python (analysis): {0}s".format(dt.datetime.now() - start))
#
# start = dt.datetime.now()
# res = df.groupby('c').rolling(20).mean()['x'] / df.groupby('c').rolling(30).mean()['y']
# print("Pandas (group by): {0}s".format(dt.datetime.now() - start))

t = MovingAverage(20, 'x')
start = dt.datetime.now()
res = t.transform(df)
print("Finance-Python (accumulator): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
res = df.rolling(20).mean()['x']
print("Pandas (group by): {0}s".format(dt.datetime.now() - start))
