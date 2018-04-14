# -*- coding: utf-8 -*-
u"""
Created on 2018-04-13

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
import numpy.matlib as matlib
from PyFin.api import CSRank

n = 3000
m = 3000

index = pd.date_range(dt.datetime(1990, 1, 1), dt.datetime(1990, 1, 1) + dt.timedelta(days=m-1))
index = np.repeat(index, n)


df = pd.DataFrame(np.random.randn(n*m, 1), columns=['x'], index=index)
ind = np.random.randint(0, int(n / 100), len(df))
df['c'] = matlib.repmat(np.linspace(0, n-1, n, dtype=int), 1, m)[0]
df['ind'] = ind

start = dt.datetime.now()
t = CSRank('x', groups='ind')
res1 = t.transform(df, category_field='c')
print("Finance-Python (analysis): {0}s".format(dt.datetime.now() - start))

start = dt.datetime.now()
df.reset_index(inplace=True)
res2 = df.groupby(['index', 'ind']).apply(lambda x: x['x'].rank() - 1)
print("Pandas (group by): {0}s".format(dt.datetime.now() - start))

res2 = pd.DataFrame({'index': res2.index.get_level_values(2), 'exp_rank': res2.values})
res2.sort_values('index', inplace=True)
res1['exp_rank'] = res2['exp_rank'].values
rank_diff = res1['transformed'] - res1['exp_rank']
print("total rank difference: {0}".format(np.abs(rank_diff).sum()))
