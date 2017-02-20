# -*- coding: utf-8 -*-
u"""
Created on 2017-1-7

@author: cheng.li
"""

import numpy as np
from scipy.optimize import least_squares
from PyFin.PricingEngines.SabrFormulaImpl import sabrVolatility
from PyFin.PricingEngines.SabrFormulaImpl import sabrVolatilities
from PyFin.PricingEngines.SabrFormulaImpl import _sabrCalibrationIteration
from PyFin.PricingEngines.SabrFormulaImpl import _parametersCheck


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
                          args=(freeParameters, strikes, volatilites, forward, expiryTime, fixedParameters))
    else:
        x = least_squares(_sabrCalibrationIteration,
                          x0,
                          method=method,
                          ftol=1e-10,
                          gtol=1e-10,
                          xtol=1e-10,
                          args=(freeParameters, strikes, volatilites, forward, expiryTime, fixedParameters))

    parameters = ['alpha', 'beta', 'nu', 'rho']
    calibratedParameters = dict(zip(freeParameters, x.x))

    res = []
    for name in parameters:
        try:
            res.append(calibratedParameters[name])
        except KeyError:
            res.append(fixedParameters[name])

    return np.array(res), x.status, x.message


__all__ = ['sabrVolatility',
           'sabrVolatilities',
           'sabrCalibration']