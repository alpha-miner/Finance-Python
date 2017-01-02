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
    data = data.sort_index()
    dummy_category = False
    if not category_field:
        category_field = 'dummy'
        data[category_field] = 1
        dummy_category = True
        total_index = list(range(len(data)))
    else:
        total_index = data.index

    total_category = data[category_field].tolist()

    matrix_values = data.as_matrix()
    columns = data.columns.tolist()

    split_category, split_values = to_dict(total_index, total_category, matrix_values, columns)

    output_values = np.zeros((len(data), len(expressions)))

    flags = [isinstance(exp, SecurityValueHolder) for exp in expressions]

    for i, exp in enumerate(expressions):

        if flags[i]:
            if not dummy_category:
                start_count = 0
                for j, dict_data in enumerate(split_values):
                    exp.push(dict_data)
                    end_count = start_count + len(dict_data)
                    output_values[start_count:end_count, i] = exp.value[split_category[j]]
                    start_count = end_count
            else:
                for j, dict_data in enumerate(split_values):
                    exp.push(dict_data)
                    output_values[j, i] = exp.value_by_name(split_category[j][0])
        else:
            output_values[:, i] = data[exp]

    df = pd.DataFrame(output_values, index=total_category, columns=cols)

    if dummy_category:
        df.index = data.index
        return df
    else:
        df[category_field] = df.index
        df.index = data.index
        return df
