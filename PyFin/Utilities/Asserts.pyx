# -*- coding: utf-8 -*-
u"""
Created on 2017-1-3

@author: cheng.li
"""

import warnings
from libc.math cimport fabs
from libc.math cimport fmax


cpdef int pyFinAssert(condition, exception, str msg="") except -1:
    if not condition:
        raise exception(msg)
    return 0


cpdef int pyEnsureRaise(exception, str msg="") except -1:
    raise exception(msg)


cpdef int pyFinWarning(condition, warn_type, str msg=""):
    if not condition:
        warnings.warn(msg, warn_type)
    return 0

cpdef bint isClose(double a, double b=0., double rel_tol=1e-09, double abs_tol=1e-12) nogil:
    return fabs(a-b) <= fmax(rel_tol * fmax(fabs(a), fabs(b)), abs_tol)
