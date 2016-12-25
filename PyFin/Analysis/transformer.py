# -*- coding: utf-8 -*-
u"""
Created on 2016-12-21

@author: cheng.li
"""

import pandas as pd
from PyFin.Utilities import to_dict
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder


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
        dict_values, category = to_dict(data_slice)
        series = []
        for exp, name in zip(expressions, cols):
            if isinstance(exp, SecurityValueHolder):
                this_series = []
                for i, dict_data in enumerate(dict_values):
                    exp.push({dict_data[0]: dict_data[1]})
                    this_series.append(exp[category[i]])
                this_series = pd.Series(this_series, index=category)
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
