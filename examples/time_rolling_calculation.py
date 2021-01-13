# -*- coding: utf-8 -*-
u"""
Created on 2021-1-12

@author: cheng.li
"""

import datetime as dt
import pandas as pd
import numpy as np
from PyFin.Math.Accumulators import (
    TimeMovingCount,
    TimeMovingCountUnique
)
from PyFin.Analysis.TechnicalAnalysis import (
    SecurityTimeMovingCount,
    SecurityTimeMovingCountUnique
)

n = 100
m = 100

index = pd.date_range(dt.datetime(2021, 1, 1), dt.datetime(2021, 1, 1) + dt.timedelta(days=m-1), freq="D")
index_total = np.repeat(index, n)

df = pd.DataFrame(np.random.randint(0, 10, (len(index_total), 3)), columns=['x', 'y', 'z'], index=index_total)
df["c"] = np.concatenate([np.linspace(0, n-1, n, dtype=int)] * len(index))
df["stamp"] = pd.DatetimeIndex(df.index).astype(np.int64) / 1e9
print(f"df.shape: {df.shape}")

start = dt.datetime.now()
exp = SecurityTimeMovingCountUnique("7D", "x") / SecurityTimeMovingCount("7D", "x")
res1 = exp.transform(df, "factor", category_field="c")
print("Finance-Python (rolling count): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
grouped = df.groupby('c')
for n, g in grouped:
    exp = TimeMovingCount("7D", "x")
    exp.transform(g)
print("Finance-Python using groupby (rolling count): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
res2 = df.groupby('c')['x'].rolling("7D").apply(lambda x: len(np.unique(x)), raw=True) \
       / df.groupby('c')['x'].rolling("7D").apply(lambda x: len(x), raw=True)
print("Pandas (rolling count): {0}s".format(dt.datetime.now() - start))

res2 = res2.sort_index(level=[1, 0]).reset_index()
np.testing.assert_array_almost_equal(res1["factor"].values, res2["x"].values)