# -*- coding: utf-8 -*-
u"""
Created on 2016-12-21

@author: cheng.li
"""

import pandas as pd


def _to_dict(raw_data):
    category = raw_data.index
    values = raw_data.values
    columns = raw_data.columns

    inner_values = [dict(zip(columns, values[i])) for i in range(len(values))]
    dict_values = dict(zip(category, inner_values))
    return dict_values, category


def transform(data, expression, col=None, category_field=None):
    data = data.copy()
    dummy_category = False
    if not category_field:
        category_field = 'dummy'
        data[category_field] = 1
        dummy_category = True

    if not col:
        col = 'user_factor'

    series = []

    for _, data_slice in data.groupby(level=0):
        data_slice = data_slice.set_index(category_field)
        dict_values, category = _to_dict(data_slice)
        expression.push(dict_values)
        series.append(expression.value[category])

    res = pd.concat(series)

    if dummy_category:
        return pd.DataFrame({col: res.values},
                            index=data.index)
    else:
        return pd.DataFrame({category_field: res.index,
                             col: res.values},
                            index=data.index)
