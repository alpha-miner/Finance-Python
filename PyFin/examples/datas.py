# -*- coding: utf-8 -*-
u"""
Created on 2016-12-25

@author: cheng.li
"""

import datetime as dt
import pandas as pd

sample_data = pd.DataFrame(
    data={'code': [1, 2, 1, 2, 1, 2],
          'open': [2.0, 1.0, 1.5, 3.0, 2.4, 3.5],
          'close': [1.7, 1.6, 0.9, 3.8, 1.6, 2.1]},
    index=[dt.datetime(2016, 1, 1),
           dt.datetime(2016, 1, 1),
           dt.datetime(2016, 1, 2),
           dt.datetime(2016, 1, 2),
           dt.datetime(2016, 1, 3),
           dt.datetime(2016, 1, 3)]
)

sample_data = sample_data[['code', 'open', 'close']]


if __name__ == '__main__':
    from PyFin.api import MA
    ts = MA(2, 'close')
    res = ts.transform(sample_data, name='ma_2_no_code')
    print(res)