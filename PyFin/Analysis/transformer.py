# -*- coding: utf-8 -*-
u"""
Created on 2016-12-21

@author: cheng.li
"""

import pandas as pd


def transform(data, expression, col=None, category_field=None):
    data = data.copy()
    dummy_category = False
    if not category_field:
        category_field = 'dummy'
        data[category_field] = 1
        dummy_category = True

    if not col:
        col = 'user_factor'

    index_list = sorted(data.index.unique())
    series = []
    for index in index_list:
        data_slice = data.ix[index]
        data_slice = data_slice.set_index(category_field)
        dict_values = data_slice.to_dict('index')
        expression.push(dict_values)
        series.append(expression.value[data_slice.index])
    res = pd.concat(series)

    if dummy_category:
        return pd.DataFrame({col: res.values},
                            index=data.index)
    else:
        return pd.DataFrame({category_field: res.index,
                             col: res.values},
                            index=data.index)