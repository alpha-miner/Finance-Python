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
    TimeMovingCountUnique,
)

n = 40000
m = 30

index = pd.date_range(dt.datetime(2021, 1, 1), dt.datetime(2021, 1, 1) + dt.timedelta(days=m-1), freq="H")
index_total = np.repeat(index, n)

df = pd.DataFrame(np.random.randint(0, 10, (len(index_total), 3)), columns=['x', 'y', 'z'], index=index_total)
df["c"] = np.concatenate([np.linspace(0, n-1, n, dtype=int)] * len(index))
df["stamp"] = pd.DatetimeIndex(df.index).astype(np.int64) / 1e9
print(f"df.shape: {df.shape}")


start = dt.datetime.now()
grouped = df.groupby("c")[["x", "stamp"]]
for g in grouped:
    exp = TimeMovingCount("7D", "x")
    res = exp.transform(g[1], "new_x")

print("Finance-Python (rolling count): {0}s".format(dt.datetime.now() - start))


start = dt.datetime.now()
res = df.groupby('c')['x'].rolling("7D").apply(lambda x: len(x), raw=True)
print("Pandas (rolling count): {0}s".format(dt.datetime.now() - start))
print(res.head())