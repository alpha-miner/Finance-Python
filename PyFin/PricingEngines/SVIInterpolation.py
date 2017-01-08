# -*- coding: utf-8 -*-
u"""
Created on 2017-1-7

@author: cheng.li
"""

import numpy as np
from scipy.optimize import least_squares
from PyFin.PricingEngines.SVIInterpolationImpl import sviVolatilityImpl


def sviVolatility(strike, forward, expiry, a, b, sigma, rho, m):
    return sviVolatilityImpl(strike, forward, expiry, a, b, sigma, rho, m)


def sviVolatilities(strikes, forward, expiry, a, b, sigma, rho, m):
    return np.array([sviVolatilityImpl(strike, forward, expiry, a, b, sigma, rho, m) for strike in strikes])


def _sviCalibrationIteration(parameters,
                             parametetsNames,
                             strikes,
                             targetVols,
                             forward,
                             expiryTime,
                             **kwargs):
    for i, name in enumerate(parametetsNames):
        kwargs[name] = parameters[i]
    return targetVols - sviVolatilities(strikes,
                                        forward,
                                        expiryTime,
                                        **kwargs)


def _parametersCheck(initialA,
                     initialB,
                     initialSigma,
                     initialRho,
                     initialM,
                     isFixedA,
                     isFixedB,
                     isFixedSigma,
                     isFixedRho,
                     isFixedM):
    x0 = []
    freeParameters = []
    fixedParameters = {}
    bounds = ([], [])

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

    x0 = np.array(x0)
    return x0, freeParameters, fixedParameters, bounds


def sviCalibration(strikes,
                   volatilites,
                   forward,
                   expiryTime,
                   initialA,
                   initialB,
                   initialSigma,
                   initialRho,
                   initialM,
                   isFixedA=False,
                   isFixedB=False,
                   isFixedSigma=False,
                   isFixedRho=False,
                   isFixedM=False,
                   method='trf'):
    x0, freeParameters, fixedParameters, bounds = _parametersCheck(initialA,
                                                                   initialB,
                                                                   initialSigma,
                                                                   initialRho,
                                                                   initialM,
                                                                   isFixedA,
                                                                   isFixedB,
                                                                   isFixedSigma,
                                                                   isFixedRho,
                                                                   isFixedM)

    if method != 'lm':
        x = least_squares(_sviCalibrationIteration,
                          x0,
                          method=method,
                          bounds=bounds,
                          ftol=1e-10,
                          gtol=1e-10,
                          xtol=1e-10,
                          args=(freeParameters, strikes, volatilites, forward, expiryTime),
                          kwargs=fixedParameters)
    else:
        x = least_squares(_sviCalibrationIteration,
                          x0,
                          method=method,
                          ftol=1e-10,
                          gtol=1e-10,
                          xtol=1e-10,
                          args=(freeParameters, strikes, volatilites, forward, expiryTime),
                          kwargs=fixedParameters)

    parameters = ['a', 'b', 'sigma', 'rho', 'm']
    calibratedParameters = dict(zip(freeParameters, x.x))

    res = []
    for name in parameters:
        try:
            res.append(calibratedParameters[name])
        except KeyError:
            res.append(fixedParameters[name])

    return np.array(res), x.status, x.message
