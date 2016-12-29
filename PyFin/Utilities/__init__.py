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


def check_date(date):
    from PyFin.DateUtilities import Date
    if isinstance(date, str):
        return Date.strptime(date, dateFormat='%Y-%m-%d')
    else:
        return Date.fromDateTime(date)


def to_dict(total_index, total_category, matrix_values, columns):

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

    return splited_category, splited_values