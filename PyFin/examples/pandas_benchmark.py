# -*- coding: utf-8 -*-
u"""
Created on 2016-12-27

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
from PyFin.api import *

# df = pd.read_csv('mtm.csv', index_col=0).sort_index()
#
# t = MA(20, 'mtm_17') / MA(30, 'mtm_27')
#
# start = dt.datetime.now()
# res = t.transform(df, category_field='productID')
# print("time elapsed: {0}s".format(dt.datetime.now() - start))
#
# start = dt.datetime.now()
# res = df.groupby('productID').rolling(20).mean()['mtm_17'] / df.groupby('productID').rolling(30).mean()['mtm_27']
# print("time elapsed: {0}s".format(dt.datetime.now() - start))


n = 200
m = 200

df = pd.DataFrame(np.random.randn(n*m, 3), columns=['x', 'y', 'z'])
df['c'] = list(range(n)) * m

index = []
for i in pd.date_range(dt.datetime(1990, 1, 1), dt.datetime(1990, 1, 1) + dt.timedelta(days=m-1)):
    index += [i] * n

df.index = index

t = MA(20, 'x') / MA(30, 'y')

start = dt.datetime.now()
res = t.transform(df, category_field='c')
print("Finance-Python (analysis): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
res = df.groupby('c').rolling(20).mean()['x'] / df.groupby('c').rolling(30).mean()['y']
print("Pandas (group by): {0}s".format(dt.datetime.now() - start))
