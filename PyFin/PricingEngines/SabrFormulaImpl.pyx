# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

cimport cython
from libc.math cimport sqrt
from libc.math cimport log
from libc.math cimport fabs
import numpy as np
cimport numpy as np
from PyFin.Math.MathConstants cimport QL_EPSILON

cdef double QL_EPSILON = QL_EPSILON

@cython.cdivision(True)
cpdef double sabrVolatility(double strike,
                            double forward,
                            double expiryTime,
                            double alpha,
                            double beta,
                            double nu,
                            double rho) nogil:
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

    if not fabs(forward - strike) < 1e-10:
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

    if fabs(z * z) > QL_EPSILON * 10:
        multiplier = z / xx
    else:
        multiplier = 1.0 - 0.5 * rho * z - (3.0 * rho * rho - 2.0) * z * z / 12.0
    return (alpha / D) * multiplier * d


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef np.ndarray[double, ndim=1] sabrVolatilities(double[:] strikes,
                     double forward,
                     double expiry,
                     double alpha,
                     double beta,
                     double nu,
                     double rho):
    cdef int i
    cdef size_t length = len(strikes)
    cdef np.ndarray[double, ndim=1] res = np.empty(length, np.float64)

    for i in range(length):
        res[i] = sabrVolatility(strikes[i], forward, expiry, alpha, beta, nu, rho)
    return res


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef np.ndarray[double, ndim=1] _sabrCalibrationIteration(double[:] parameters,
                              list parametetsNames,
                              double[:] strikes,
                              double[:] targetVols,
                              double forward,
                              double expiryTime,
                              dict argDict):
    cdef int i
    cdef str name
    for i, name in enumerate(parametetsNames):
        argDict[name] = parameters[i]
    return targetVols - sabrVolatilities(strikes,
                                         forward,
                                         expiryTime,
                                         **argDict)


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef _parametersCheck(double intialAlpha,
                       double initialBeta,
                       double initialNu,
                       double initialRho,
                       bint isFixedAlpha,
                       bint isFixedBeta,
                       bint isFixedNu,
                       bint isFixedRho):
    cdef list x0 = []
    cdef list freeParameters = []
    cdef dict fixedParameters = {}
    cdef tuple bounds = ([], [])

    if isFixedAlpha:
        fixedParameters['alpha'] = intialAlpha
    else:
        freeParameters.append('alpha')
        x0.append(intialAlpha)
        bounds[0].append(0.)
        bounds[1].append(np.inf)

    if isFixedBeta:
        fixedParameters['beta'] = initialBeta
    else:
        freeParameters.append('beta')
        x0.append(initialBeta)
        bounds[0].append(0.)
        bounds[1].append(1.)

    if isFixedNu:
        fixedParameters['nu'] = initialNu
    else:
        freeParameters.append('nu')
        x0.append(initialNu)
        bounds[0].append(0.)
        bounds[1].append(np.inf)

    if isFixedRho:
        fixedParameters['rho'] = initialRho
    else:
        freeParameters.append('rho')
        x0.append(initialRho)
        bounds[0].append(-1.)
        bounds[1].append(1.0)

    return np.array(x0), freeParameters, fixedParameters, bounds
