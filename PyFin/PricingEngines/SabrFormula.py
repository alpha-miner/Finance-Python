# -*- coding: utf-8 -*-
u"""
Created on 2017-1-7

@author: cheng.li
"""

import numpy as np
from scipy.optimize import least_squares
from PyFin.PricingEngines.SabrFormulaImpl import sabrVolatilityImpl


def sabrVolatility(strike,
                   forward,
                   expiryTime,
                   alpha,
                   beta,
                   nu,
                   rho):
    return sabrVolatilityImpl(strike, forward, expiryTime, alpha, beta, nu, rho)


def sabrVolatilities(strikes,
                     forward,
                     expiryTime,
                     alpha,
                     beta,
                     nu,
                     rho):
    return np.array([sabrVolatilityImpl(strike, forward, expiryTime, alpha, beta, nu, rho) for strike in strikes])


def _sabrCalibrationIteration(parameters,
                              parametetsNames,
                              strikes,
                              targetVols,
                              forward,
                              expiryTime,
                              **kwargs):
    for i, name in enumerate(parametetsNames):
        kwargs[name] = parameters[i]
    return targetVols - sabrVolatilities(strikes,
                                         forward,
                                         expiryTime,
                                         **kwargs)


def _parametersCheck(intialAlpha,
                     initialBeta,
                     initialNu,
                     initialRho,
                     isFixedAlpha,
                     isFixedBeta,
                     isFixedNu,
                     isFixedRho):
    x0 = []
    freeParameters = []
    fixedParameters = {}
    bounds = ([], [])

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

    x0 = np.array(x0)
    return x0, freeParameters, fixedParameters, bounds


def sabrCalibration(strikes,
                    volatilites,
                    forward,
                    expiryTime,
                    intialAlpha,
                    initialBeta,
                    initialNu,
                    initialRho,
                    isFixedAlpha=False,
                    isFixedBeta=False,
                    isFixedNu=False,
                    isFixedRho=False,
                    method='trf'):

    x0, freeParameters, fixedParameters, bounds = _parametersCheck(intialAlpha,
                                                                   initialBeta,
                                                                   initialNu,
                                                                   initialRho,
                                                                   isFixedAlpha,
                                                                   isFixedBeta,
                                                                   isFixedNu,
                                                                   isFixedRho)

    if method != 'lm':
        x = least_squares(_sabrCalibrationIteration,
                          x0,
                          method=method,
                          bounds=bounds,
                          ftol=1e-10,
                          gtol=1e-10,
                          xtol=1e-10,
                          args=(freeParameters, strikes, volatilites, forward, expiryTime),
                          kwargs=fixedParameters)
    else:
        x = least_squares(_sabrCalibrationIteration,
                          x0,
                          method=method,
                          ftol=1e-10,
                          gtol=1e-10,
                          xtol=1e-10,
                          args=(freeParameters, strikes, volatilites, forward, expiryTime),
                          kwargs=fixedParameters)

    parameters = ['alpha', 'beta', 'nu', 'rho']
    calibratedParameters = dict(zip(freeParameters, x.x))

    res = []
    for name in parameters:
        try:
            res.append(calibratedParameters[name])
        except KeyError:
            res.append(fixedParameters[name])

    return np.array(res), x.status, x.message
