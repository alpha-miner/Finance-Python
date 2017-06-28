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
from PyFin.PricingEngines import sviVolatility as svi
from PyFin.PricingEngines import sviVolatilities as svis
from PyFin.PricingEngines import sviCalibration as svic


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
@xw.arg('volatilites', np.array, dim=1)
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


@xw.func
def sviVolatility(strike, forward, expiry, a, b, sigma, rho, m):
    return svi(strike, forward, expiry, a, b, sigma, rho, m)


@xw.func
@xw.ret(expand='table')
@xw.arg('strikes', np.array, dim=1)
def sviVolatilities(strikes, forward, expiry, a, b, sigma, rho, m):
    return svis(strikes, forward, expiry, a, b, sigma, rho, m)


@xw.func
@xw.ret(expand='table')
@xw.arg('strikes', np.array, dim=1)
@xw.arg('volatilites', np.array, dim=1)
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
    x = svic(strikes,
             volatilites,
             forward,
             expiryTime,
             initialA,
             initialB,
             initialSigma,
             initialRho,
             initialM,
             isFixedA,
             isFixedB,
             isFixedSigma,
             isFixedRho,
             isFixedM,
             method)
    return x[0]
