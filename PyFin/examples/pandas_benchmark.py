# -*- coding: utf-8 -*-
u"""
Created on 2016-12-27

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
from PyFin.api import *

n = 800
m = 20


df = pd.DataFrame(np.random.randn(n*m, 3), columns=['x', 'y', 'z'])
df['c'] = list(range(n)) * m

index = []
for i in range(m):
    index += [i] * n

df.index = index

t = MA(2, 'x')

start = dt.datetime.now()
res = t.transform(df, category_field='c')
print("time elapsed: {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
res = df.groupby('c').rolling(2).mean()['x']
print("time elapsed: {0}s".format(dt.datetime.now() - start))

