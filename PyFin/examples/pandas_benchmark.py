# -*- coding: utf-8 -*-
u"""
Created on 2016-12-27

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
from PyFin.api import MA

df = pd.DataFrame(np.random.randn(800*752, 1), columns=['x'])
df['c'] = list(range(800)) * 752

t = MA(2, 'x')

start = dt.datetime.now()
t.transform(df, category_field='c')
print("time elapsed: {0}s".format(dt.datetime.now() - start))