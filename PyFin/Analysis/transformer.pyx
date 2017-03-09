# -*- coding: utf-8 -*-
u"""
Created on 2017-2-15

@author: cheng.li
"""

import numpy as np
cimport numpy as np
import pandas as pd
cimport cython
from PyFin.Utilities.Tools import to_dict
from PyFin.Analysis.SecurityValueHolders cimport SecurityValueHolder


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef transform(data, list expressions, list cols, str category_field=None, bint to_sort=False, bint dropna=True):

    cdef int dummy_category
    cdef int i
    cdef int j
    cdef np.ndarray total_category
    cdef double[:, :] matrix_values
    cdef double[:, :] output_values
    cdef double[:] narr_view
    cdef int start_count
    cdef int end_count
    cdef list flags
    cdef list split_category
    cdef list split_values
    cdef SecurityValueHolder exp
    cdef dict dict_data

    if to_sort:
            data.sort_index(inplace=True)

    dummy_category = 0
    if not category_field:
        category_field = 'dummy'
        data[category_field] = 1
        dummy_category = 1
        total_index = list(range(len(data)))
    else:
        total_index = data.index

    total_category = data[category_field].values
    data = data.select_dtypes([np.number])
    matrix_values = data.as_matrix()
    columns = data.columns.tolist()

    split_category, split_values = to_dict(total_index, total_category.tolist(), matrix_values, columns)

    output_values = np.zeros((len(data), len(expressions)))

    flags = [isinstance(e, SecurityValueHolder) for e in expressions]

    for i, e in enumerate(expressions):

        if flags[i]:
            if not dummy_category:
                start_count = 0
                for j, dict_data in enumerate(split_values):
                    exp = e
                    exp.push(dict_data)
                    end_count = start_count + len(dict_data)
                    narr_view = exp.value_by_names(split_category[j]).values
                    output_values[start_count:end_count, i] = narr_view
                    start_count = end_count
            else:
                for j, dict_data in enumerate(split_values):
                    exp = e
                    exp.push(dict_data)
                    output_values[j, i] = exp.value_by_name(split_category[j][0])
        else:
            narr_view = data[e].values
            output_values[:, i] = narr_view

    df = pd.DataFrame(np.array(output_values), index=data.index, columns=cols)
    if not dummy_category:
        df[category_field] = total_category

    if dropna:
        df.dropna(inplace=True)

    return df
