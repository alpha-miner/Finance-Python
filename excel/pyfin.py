# -*- coding: utf-8 -*-
u"""
Created on 2017-1-7

@author: cheng.li
"""

import xlwings as xw
import numpy as np
from PyFin.PricingEngines import sabrVolatility as sbv
from PyFin.PricingEngines import sabrVolatilities as sbvs
from PyFin.PricingEngines import sabrCalibration as scb


@xw.func
def sabrVolatility(strike, forward, expiry, alpha, beta, nu, rho):
    return sbv(strike, forward, expiry, alpha, beta, nu, rho)

@xw.func
@xw.ret(expand='table')
@xw.arg('strikes', np.array, dim=1)
def sabrVolatilities(strikes, forward, expiry, alpha, beta, nu, rho):
    return sbvs(strikes, forward, expiry, alpha, beta, nu, rho)


@xw.func
@xw.ret(expand='table')
@xw.arg('strikes', np.array, dim=1)
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
    x = scb(strikes,
            volatilites,
            forward,
            expiryTime,
            intialAlpha,
            initialBeta,
            initialNu,
            initialRho,
            isFixedAlpha,
            isFixedBeta,
            isFixedNu,
            isFixedRho,
            method)
    return x[0]