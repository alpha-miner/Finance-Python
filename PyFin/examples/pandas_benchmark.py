# -*- coding: utf-8 -*-
u"""
Created on 2016-12-27

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
from PyFin.api import *

df = pd.DataFrame(np.random.randn(800*752, 1), columns=['x'])
df['c'] = list(range(800)) * 752

index = []
for i in range(752):
    index += [i] * 800

df.index = index


t = MA(2, 'x')

start = dt.datetime.now()
res = t.transform(df, category_field='c')
print("time elapsed: {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
res = df.groupby('c').rolling(2).mean()
print("time elapsed: {0}s".format(dt.datetime.now() - start))

