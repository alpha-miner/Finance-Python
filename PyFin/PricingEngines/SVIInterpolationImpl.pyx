# -*- coding: utf-8 -*-
u"""
Created on 2017-1-8

@author: cheng.li
"""

import cython
from libc.math cimport sqrt
from libc.math cimport log
import numpy as np
cimport numpy as np

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

@cython.boundscheck(False)
cpdef np.ndarray[double, ndim=1]  sviVolatilitiesImpl(double[:] strikes,
                                     double forward,
                                     double expiry,
                                     double a,
                                     double b,
                                     double sigma,
                                     double rho,
                                     double m):
    cdef int length = len(strikes)
    cdef np.ndarray[double, ndim=1] res = np.empty(length, np.float64)

    for i in range(length):
        res[i] = sviVolatilityImpl(strikes[i], forward, expiry, a, b, sigma, rho, m)
    return res
