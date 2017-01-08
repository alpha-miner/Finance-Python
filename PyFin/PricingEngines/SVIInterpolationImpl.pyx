# -*- coding: utf-8 -*-
u"""
Created on 2017-1-8

@author: cheng.li
"""

import cython
from libc.math cimport sqrt
from libc.math cimport log

@cython.cdivision(True)
cpdef double sviVolatilityImpl(double strike,
                               double forward,
                               double expiry,
                               double a,
                               double b,
                               double sigma,
                               double rho,
                               double m):
    k = log(strike / forward)
    totalVairance = a + b * (rho * (k - m) + sqrt((k - m) * (k - m) + sigma * sigma))
    return sqrt(totalVairance / expiry)
