# -*- coding: utf-8 -*-
u"""
Created on 2016-12-21

@author: cheng.li
"""

import numpy as np
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

    index_line = data.index.unique()
    total_category = data[category_field]
    values = np.zeros((len(data), len(expressions)))

    splited_values = {}
    for date in index_line:
        data_slice = data.ix[date]
        if not isinstance(data_slice, pd.Series):
            data_slice = data_slice.set_index(category_field)
            dict_values, category = to_dict(data_slice)
            splited_values[date] = (dict_values, category)
        else:
            splited_values[date] = ({data_slice.name: data_slice.to_dict()}, [data_slice[category_field]])

    for i, exp in enumerate(expressions):
        if isinstance(exp, SecurityValueHolder):
            start_count = 0
            for j, date in enumerate(index_line):
                category = splited_values[date][1]
                exp.push(splited_values[date][0])
                end_count = start_count + len(category)
                values[start_count:end_count, i] = exp.value[category]
                start_count = end_count
        else:
            values[:, i] = data[exp]
    df = pd.DataFrame(values, index=total_category, columns=cols)

    if dummy_category:
        df.index = data.index
        return df
    else:
        df[category_field] = df.index
        df.index = data.index
        return df
