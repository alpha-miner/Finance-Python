# -*- coding: utf-8 -*-
u"""
Created on 2016-12-21

@author: cheng.li
"""

import pandas as pd
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


def _to_dict(raw_data):
    category = raw_data.index
    values = raw_data.values
    columns = raw_data.columns

    inner_values = [dict(zip(columns, values[i])) for i in range(len(values))]
    dict_values = dict(zip(category, inner_values))
    return dict_values, category


def transform(data, expressions, cols, category_field=None):
    data = data.copy()
    dummy_category = False
    if not category_field:
        category_field = 'dummy'
        data[category_field] = 1
        dummy_category = True

    dfs = []

    for _, data_slice in data.groupby(level=0):
        data_slice = data_slice.set_index(category_field)
        dict_values, category = _to_dict(data_slice)
        series = []
        for exp, name in zip(expressions, cols):
            if isinstance(exp, SecurityValueHolder):
                exp.push(dict_values)
                this_series = exp.value[category]
                this_series.name = name
            else:
                this_series = data_slice[exp]
                this_series.name = name
            series.append(this_series)
        df = pd.concat(series, axis=1)
        dfs.append(df)

    res = pd.concat(dfs)

    if dummy_category:
        res.index = data.index
        return res
    else:
        res[category_field] = res.index
        res.index = data.index
        return res
