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

    total_index = data.index
    total_category = data[category_field].values

    output_values = np.zeros((len(data), len(expressions)))

    matrix_values = data.as_matrix()
    columns = data.columns

    splited_values = []
    splited_category = []
    n = np.size(matrix_values, 0)
    current_dict = {}
    current_category = []
    previous_index = total_index[0]
    for i in range(n):
        key = total_category[i]
        if total_index[i] != previous_index:
            splited_values.append(current_dict)
            splited_category.append(current_category)
            current_dict = {}
            current_category = []
        current_dict[key] = dict(zip(columns, matrix_values[i, :]))
        current_category.append(key)
    splited_values.append(current_dict)
    splited_category.append(current_category)

    for i, exp in enumerate(expressions):
        if isinstance(exp, SecurityValueHolder):
            start_count = 0
            for j, dict_data in enumerate(splited_values):
                exp.push(dict_data)
                end_count = start_count + len(dict_data)
                output_values[start_count:end_count, i] = exp.value[splited_category[j]]
                start_count = end_count
        else:
            output_values[:, i] = data[exp]
    df = pd.DataFrame(output_values, index=total_category, columns=cols)

    if dummy_category:
        df.index = total_index
        return df
    else:
        df[category_field] = df.index
        df.index = total_index
        return df
