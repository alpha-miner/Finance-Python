# -*- coding: utf-8 -*-
u"""
Created on 2017-6-8

@author: cheng.li
"""

cdef inline double sign(double x) nogil:
    if x > 0.:
        return 1.
    elif x < 0.:
        return -1.
    else:
        return 0.


cdef inline double consecutive_int_sum(double s, double e) nogil:
    return (e + s) * (e - s + 1.) / 2.
