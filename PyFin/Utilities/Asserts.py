# -*- coding: utf-8 -*-
u"""
Created on 2015-8-17

@author: cheng.li
"""


def pyFinAssert(condition, exception, msg=""):
    if not condition:
        raise exception(msg)


def isClose(a, b=0., rel_tol=1e-09, abs_tol=1e-12):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
