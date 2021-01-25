# -*- coding: utf-8 -*-
u"""
Created on 2015-8-17

@author: cheng.li
"""

import time
from PyFin.Utilities.Asserts import require
from PyFin.Utilities.Asserts import ensureRaise
from PyFin.Utilities.Asserts import warning
from PyFin.Utilities.Asserts import isClose

__all__ = ['require',
           'ensureRaise',
           'warning',
           'isClose']


def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        return t2 - t1, res
    return wrapper






