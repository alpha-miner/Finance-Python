# -*- coding: utf-8 -*-
u"""
Created on 2017-1-8

@author: cheng.li
"""

cimport cython
from libc.math cimport sqrt
from libc.math cimport log
import numpy as np
cimport numpy as np

@cython.cdivision(True)
cpdef double sviVolatility(double strike,
                               double forward,
                               double expiry,
                               double a,
                               double b,
                               double sigma,
                               double rho,
                               double m) nogil:
    k = log(strike / forward)
    totalVairance = a + b * (rho * (k - m) + sqrt((k - m) * (k - m) + sigma * sigma))
    return sqrt(totalVairance / expiry)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef np.ndarray[double, ndim=1]  sviVolatilities(double[:] strikes,
                                     double forward,
                                     double expiry,
                                     double a,
                                     double b,
                                     double sigma,
                                     double rho,
                                     double m):
    cdef int i
    cdef size_t length = len(strikes)
    cdef np.ndarray[double, ndim=1] res = np.empty(length, np.float64)

    for i in range(length):
        res[i] = sviVolatility(strikes[i], forward, expiry, a, b, sigma, rho, m)
    return res


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef np.ndarray[double, ndim=1] _sviCalibrationIteration(double[:] parameters,
                             list parametetsNames,
                             double[:] strikes,
                             double[:] targetVols,
                             double forward,
                             double expiryTime,
                             dict argsDict):

    cdef int i
    cdef str name

    for i, name in enumerate(parametetsNames):
        argsDict[name] = parameters[i]
    return targetVols - sviVolatilities(strikes,
                                        forward,
                                        expiryTime,
                                        **argsDict)


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef _parametersCheck(double initialA,
                     double initialB,
                     double initialSigma,
                     double initialRho,
                     double initialM,
                     bint isFixedA,
                     bint isFixedB,
                     bint isFixedSigma,
                     bint isFixedRho,
                     bint isFixedM):
    cdef list x0 = []
    cdef list freeParameters = []
    cdef dict fixedParameters = {}
    cdef tuple bounds = ([], [])

    if isFixedA:
        fixedParameters['a'] = initialA
    else:
        freeParameters.append('a')
        x0.append(initialA)
        bounds[0].append(-np.inf)
        bounds[1].append(np.inf)

    if isFixedB:
        fixedParameters['b'] = initialB
    else:
        freeParameters.append('b')
        x0.append(initialB)
        bounds[0].append(0.)
        bounds[1].append(np.inf)

    if isFixedSigma:
        fixedParameters['sigma'] = initialSigma
    else:
        freeParameters.append('sigma')
        x0.append(initialSigma)
        bounds[0].append(0.)
        bounds[1].append(np.inf)

    if isFixedRho:
        fixedParameters['rho'] = initialRho
    else:
        freeParameters.append('rho')
        x0.append(initialRho)
        bounds[0].append(-1.)
        bounds[1].append(1.0)

    if isFixedM:
        fixedParameters['m'] = initialM
    else:
        freeParameters.append('m')
        x0.append(initialRho)
        bounds[0].append(-np.inf)
        bounds[1].append(np.inf)

    return np.array(x0), freeParameters, fixedParameters, bounds

