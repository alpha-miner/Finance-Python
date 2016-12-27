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

    data_slice = data.set_index(category_field)
    dict_values, category = to_dict(data_slice)

    values = np.zeros((len(data_slice), len(expressions)))

    for i, exp in enumerate(expressions):
        if isinstance(exp, SecurityValueHolder):
            for j, dict_data in enumerate(dict_values):
                exp.push_one(dict_data[0], dict_data[1])
                values[j, i] = exp[category[j]]
        else:
            values[:, i] = data_slice[exp]
    df = pd.DataFrame(values, index=category, columns=cols)

    if dummy_category:
        df.index = data.index
        return df
    else:
        df[category_field] = df.index
        df.index = data.index
        return df
