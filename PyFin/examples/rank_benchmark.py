# -*- coding: utf-8 -*-
u"""
Created on 2018-04-13

@author: cheng.li
"""

import datetime as dt
import numpy as np
from PyFin.Analysis.SeriesValues import SeriesValues


data = np.random.randn(50000)
groups = np.random.randint(0, 300, 50000)
index = list(range(50000))
n_loops = 1000

data = SeriesValues(data, index=index)
groups = SeriesValues(groups, index=index)

start = dt.datetime.now()
for _ in range(n_loops):
    res1 = data.rank()
print("Rank: {0}s".format(dt.datetime.now() - start))


start = dt.datetime.now()
for _ in range(n_loops):
    res2 = data.rank(groups)
print("Rank with group: {0}s".format(dt.datetime.now() - start))

print(res1.values)
print(res2.values)


