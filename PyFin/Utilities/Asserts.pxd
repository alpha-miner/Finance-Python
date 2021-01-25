# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cpdef int require(condition, exception, str msg=*) except -1

cpdef int ensureRaise(exception, str msg=*) except -1

cpdef int warning(condition, warn_type, str msg=*)

cpdef bint isClose(double a, double b=*, double rel_tol=*, double abs_tol=*) nogil