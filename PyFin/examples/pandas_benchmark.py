# -*- coding: utf-8 -*-
u"""
Created on 2016-12-27

@author: cheng.li
"""

import datetime as dt
import numpy as np
import numpy.matlib as matlib
import pandas as pd
from PyFin.api import *
from PyFin.Math.Accumulators import MovingAverage

n = 300
m = 300

index = pd.date_range(dt.datetime(1990, 1, 1), dt.datetime(1990, 1, 1) + dt.timedelta(days=m-1))
index = np.repeat(index, n)

df = pd.DataFrame(np.random.randn(n*m, 3), columns=['x', 'y', 'z'], index=index)
df['c'] = matlib.repmat(np.linspace(0, n-1, n, dtype=int), 1, m)[0]

start = dt.datetime.now()
t = MA(20, 'x') / MA(30, 'y')
res = t.transform(df, category_field='c')
print("Finance-Python (group ma): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
groups = df.groupby('c')
res = groups['x'].rolling(20).mean() / groups['y'].rolling(30).mean()
print("Pandas (group ma): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
t = MovingAverage(20, 'x') / MovingAverage(30, 'x')
res = t.transform(df)
print("\nFinance-Python (rolling ma): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
res = df['x'].rolling(20).mean() / df['x'].rolling(30).mean()
print("Pandas (rolling ma): {0}s".format(dt.datetime.now() - start))


"""
Cross section analysis examples ...
"""

# rank

index = pd.date_range(dt.datetime(1990, 1, 1), dt.datetime(1990, 1, 1) + dt.timedelta(days=m-1))
index = np.repeat(index, n)

df = pd.DataFrame(np.random.randn(n*m, 1), columns=['x'], index=index)
ind = np.random.randint(0, int(n / 100), len(df))
df['c'] = matlib.repmat(np.linspace(0, n-1, n, dtype=int), 1, m)[0]
df['ind'] = ind

start = dt.datetime.now()
t = CSRank('x', groups='ind')
res1 = t.transform(df, category_field='c')
print("\nFinance-Python (cs rank): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
df2 = df.reset_index()
res2 = df2.groupby(['index', 'ind']).apply(lambda x: x['x'].rank())
print("Pandas (cs rank): {0}s".format(dt.datetime.now() - start))

res2 = pd.DataFrame({'index': res2.index.get_level_values(2), 'exp_rank': res2.values})
res2.sort_values('index', inplace=True)
res1['exp_rank'] = res2['exp_rank'].values
diff = res1['transformed'] - res1['exp_rank']
print("total rank difference: {0}".format(np.abs(diff).sum()))

# percentile

start = dt.datetime.now()
t = CSQuantiles('x', groups='ind')
res1 = t.transform(df, category_field='c')
print("\nFinance-Python (cs percentile): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
df2 = df.reset_index()
res2 = df2.groupby(['index', 'ind']).apply(lambda x: x['x'].rank() / (len(x) + 1))
print("Pandas (cs percentile): {0}s".format(dt.datetime.now() - start))

res2 = pd.DataFrame({'index': res2.index.get_level_values(2), 'exp_rank': res2.values})
res2.sort_values('index', inplace=True)
res1['exp_rank'] = res2['exp_rank'].values
diff = res1['transformed'] - res1['exp_rank']
print("total percentile difference: {0}".format(np.abs(diff).sum()))

# zscore

start = dt.datetime.now()
t = CSZScore('x', groups='ind')
res1 = t.transform(df, category_field='c')
print("\nFinance-Python (cs zscore): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
df2 = df.reset_index()
res2 = df2.groupby(['index', 'ind']).apply(lambda x: (x['x'] - x['x'].mean()) / x['x'].std(ddof=0))
print("Pandas (cs zscore): {0}s".format(dt.datetime.now() - start))

res2 = pd.DataFrame({'index': res2.index.get_level_values(2), 'exp_rank': res2.values})
res2.sort_values('index', inplace=True)
res1['exp_rank'] = res2['exp_rank'].values
diff = res1['transformed'] - res1['exp_rank']
print("total zscore difference: {0}".format(np.abs(diff).sum()))