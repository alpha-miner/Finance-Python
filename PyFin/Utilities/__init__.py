# -*- coding: utf-8 -*-
u"""
Created on 2015-8-17

@author: cheng.li
"""

import time
import numpy as np
from PyFin.Utilities.Asserts import pyFinAssert
from PyFin.Utilities.Asserts import isClose

__all__ = ['pyFinAssert',
           'isClose']


def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        return t2 - t1, res
    return wrapper


def to_dict(total_index, total_category, matrix_values, columns):

    index_diff_loc = np.where(np.diff(total_index))[0]

    splited_values = []
    splited_category = []

    start = 0
    for i, end in enumerate(index_diff_loc):
        splited_category.append(total_category[start:end+1])
        current_dict = {total_category[j]: {k: v for k, v in zip(columns, matrix_values[j])} for j in range(start, end+1)}
        splited_values.append(current_dict)
        start = end + 1

    splited_category.append(total_category[start:])
    current_dict = {total_category[j]: {k: v for k, v in zip(columns, matrix_values[j])} for j in
                    range(start, len(total_category))}
    splited_values.append(current_dict)

    return splited_category, splited_values





