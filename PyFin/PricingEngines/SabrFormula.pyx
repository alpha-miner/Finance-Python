# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

import cython
from libc.math cimport sqrt
from libc.math cimport log
from PyFin.Math.MathConstants import MathConstants

cdef double QL_EPSILON

QL_EPSILON = MathConstants.QL_EPSILON

@cython.cdivision(True)
def sabrVolatility(double strike,
                   double forward,
                   double expiryTime,
                   double alpha,
                   double beta,
                   double nu,
                   double rho):
    cdef double oneMinusBeta
    cdef double A
    cdef double sqrtA
    cdef double logM
    cdef double epsilon
    cdef double z
    cdef double B
    cdef double C
    cdef double tmp
    cdef double xx
    cdef double D
    cdef double d
    cdef double multiplier

    oneMinusBeta = 1.0 - beta
    A = (forward * strike) ** oneMinusBeta
    sqrtA = sqrt(A)
    if not abs(forward - strike) < 1e-10:
        logM = log(forward / strike)

    else:
        epsilon = (forward - strike) / strike
        logM = epsilon - .5 * epsilon * epsilon
    z = (nu / alpha) * sqrtA * logM
    B = 1.0 - 2.0 * rho * z + z * z
    C = oneMinusBeta * oneMinusBeta * logM * logM
    tmp = (sqrt(B) + z - rho) / (1.0 - rho)
    xx = log(tmp)
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
