# -*- coding: utf-8 -*-
u"""
Created on 2016-12-27

@author: cheng.li
"""

import datetime as dt
import numpy as np
import numpy.matlib as matlib
import pandas as pd
from PyFin.api import MA
from PyFin.api import LAST
from PyFin.Math.Accumulators import MovingAverage
from PyFin.Math.Accumulators import Latest

n = 3000
m = 3000

index = pd.date_range(dt.datetime(1990, 1, 1), dt.datetime(1990, 1, 1) + dt.timedelta(days=m-1))
index = np.repeat(index, n)

df = pd.DataFrame(np.random.randn(n*m, 3), columns=['x', 'y', 'z'], index=index)
df['c'] = matlib.repmat(np.linspace(0, n-1, n, dtype=int), 1, m)[0]

start = dt.datetime.now()
t = MA(20, 'x') / MA(30, 'y')
res = t.transform(df, category_field='c')
print("Finance-Python (analysis): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
groups = df.groupby('c')
res = groups['x'].rolling(20).mean() / groups['y'].rolling(30).mean()
print("Pandas (group by): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
t = MovingAverage(20, 'x') / MovingAverage(30, 'x')
res = t.transform(df)
print("Finance-Python (accumulator): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
res = df['x'].rolling(20).mean() / df['x'].rolling(30).mean()
print("Pandas (group by): {0}s".format(dt.datetime.now() - start))