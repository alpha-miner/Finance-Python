# -*- coding: utf-8 -*-
u"""
Created on 2017-1-22

@author: cheng.li
"""

import cython
import numpy as np
cimport numpy as np

@cython.boundscheck(False)
def to_dict(total_index, list total_category, double[:, :] matrix_values, list columns):

    cdef long start = 0
    cdef int i
    cdef long end
    cdef int k
    cdef int j

    cdef dict current_dict
    cdef list index_diff_loc = list(np.where(np.diff(total_index))[0])
    cdef list splited_values = []
    cdef list splited_category = []
    cdef list column_index = list(range(len(columns)))

    for i, end in enumerate(index_diff_loc):
        splited_category.append(total_category[start:end+1])
        current_dict = {total_category[j]: {columns[k]: matrix_values[j, k] for k in column_index} for j in range(start, end+1)}
        splited_values.append(current_dict)
        start = end + 1

    splited_category.append(total_category[start:])
    current_dict = {total_category[j]: {columns[k]: matrix_values[j, k] for k in column_index} for j in
                    range(start, len(total_category))}
    splited_values.append(current_dict)

    return splited_category, splited_values