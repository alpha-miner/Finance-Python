# -*- coding: utf-8 -*-
u"""
Created on 2015-8-17

@author: cheng.li
"""

import time
from PyFin.Utilities.Asserts import pyFinAssert

__all__ = ['pyFinAssert']


def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        return t2 - t1, res
    return wrapper
