# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cpdef pyFinAssert(condition, exception, str msg=*)

cpdef pyFinWarning(condition, warn_type, str msg=*)

cpdef isClose(float a, float b=*, float rel_tol=*, float abs_tol=*)