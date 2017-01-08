# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

import cython
from libc.math cimport sqrt
from libc.math cimport log
import numpy as np
cimport numpy as np
from PyFin.Math.MathConstants import MathConstants

cdef double QL_EPSILON = MathConstants.QL_EPSILON

@cython.cdivision(True)
cpdef double sabrVolatilityImpl(double strike,
                        double forward,
                        double expiryTime,
                        double alpha,
                        double beta,
                        double nu,
                        double rho):
    cdef double oneMinusBeta = 1.0 - beta
    cdef double A = (forward * strike) ** oneMinusBeta
    cdef double sqrtA = sqrt(A)

    cdef double logM
    cdef double epsilon
    cdef double z
    cdef double B
    cdef double C
    cdef double xx
    cdef double D
    cdef double d
    cdef double multiplier

    if not abs(forward - strike) < 1e-10:
        logM = log(forward / strike)

    else:
        epsilon = (forward - strike) / strike
        logM = epsilon * (1. - .5 * epsilon)
    z = (nu / alpha) * sqrtA * logM
    B = 1.0 - (2.0 * rho - z) * z
    C = oneMinusBeta * oneMinusBeta * logM * logM
    xx = log((sqrt(B) + z - rho) / (1.0 - rho))
    D = sqrtA * (1.0 + C / 24.0 + C * C / 1920.0)
    d = 1.0 + expiryTime * \
              (oneMinusBeta * oneMinusBeta * alpha * alpha / (24.0 * A)
               + 0.25 * rho * beta * nu * alpha / sqrtA
               + (2.0 - 3.0 * rho * rho) * (nu * nu / 24.0))

    if abs(z * z) > QL_EPSILON * 10:
        multiplier = z / xx
    else:
        multiplier = 1.0 - 0.5 * rho * z - (3.0 * rho * rho - 2.0) * z * z / 12.0
    return (alpha / D) * multiplier * d


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef np.ndarray[double, ndim=1] sabrVolatilitiesImpl(np.ndarray[double, ndim=1] strikes,
                     double forward,
                     double expiry,
                     double alpha,
                     double beta,
                     double nu,
                     double rho):
    cdef int i
    cdef int length = len(strikes)
    cdef np.ndarray[double, ndim=1] res = np.empty(length, np.float64)

    for i in range(length):
        res[i] = sabrVolatilityImpl(strikes[i], forward, expiry, alpha, beta, nu, rho)
    return res
