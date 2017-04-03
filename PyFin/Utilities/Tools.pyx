# -*- coding: utf-8 -*-
u"""
Created on 2017-1-22

@author: cheng.li
"""

cimport cython
import numpy as np
cimport numpy as np
from PyFin.Utilities.Asserts cimport pyFinAssert

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef to_dict(total_index, list total_category, double[:, :] matrix_values, list columns):

    cdef long start = 0
    cdef int i
    cdef long end
    cdef int k
    cdef int j

    cdef dict current_dict = {}
    cdef list index_diff_loc = list(np.where(np.diff(total_index))[0])
    cdef size_t index_diff_length = len(index_diff_loc)
    cdef list splited_values = [None] * (index_diff_length + 1)
    cdef list splited_category = [None] * (index_diff_length + 1)
    cdef size_t column_length = len(columns)

    for i in range(index_diff_length):
        end = index_diff_loc[i]
        splited_category[i] = total_category[start:end+1]
        current_dict = {}
        for j in range(start, end+1):
            current_dict[total_category[j]] = {columns[k]: matrix_values[j, k] for k in range(column_length)}
        splited_values[i] = current_dict
        start = end + 1

        pyFinAssert(len(current_dict) == len(splited_category[i]),
                    ValueError,
                    "There is duplicated category value in the snapshot ({0})".format(total_index[start]))

    splited_category[index_diff_length] = total_category[start:]
    current_dict = {}
    for j in range(start, len(total_category)):
        current_dict[total_category[j]] = {columns[k]: matrix_values[j, k] for k in range(column_length)}
    splited_values[index_diff_length] = current_dict

    return splited_category, splited_values