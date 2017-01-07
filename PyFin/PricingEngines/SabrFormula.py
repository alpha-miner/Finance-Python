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
                              strikes,
                              targetVols,
                              forward,
                              expiryTime):
    return targetVols - sabrVolatilities(strikes,
                                       forward,
                                       expiryTime,
                                       parameters[0],
                                       parameters[1],
                                       parameters[2],
                                       parameters[3])


def sabrCalibration(strikes,
                    volatilites,
                    forward,
                    expiryTime,
                    intialAlpha,
                    initialBeta,
                    initialNu,
                    initialRho,
                    method='trf'):
    x0 = np.array([intialAlpha, initialBeta, initialNu, initialRho])
    if method != 'lm':
        x = least_squares(_sabrCalibrationIteration,
                          x0,
                          method=method,
                          bounds=([0., 0., 0., -1.], [np.inf, 1, np.inf, 1.]),
                          ftol=1e-10,
                          gtol=1e-10,
                          xtol=1e-10,
                          args=(strikes, volatilites, forward, expiryTime))
    else:
        x = least_squares(_sabrCalibrationIteration,
                          x0,
                          method=method,
                          ftol=1e-10,
                          gtol=1e-10,
                          xtol=1e-10,
                          args=(strikes, volatilites, forward, expiryTime))
    return x.x, x.status, x.message
