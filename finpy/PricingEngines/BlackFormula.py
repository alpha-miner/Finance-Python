# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

from finpy.Enums.OptionType import OptionType
from finpy.Math.Distributions.NormalDistribution import CumulativeNormalDistribution
from finpy.Math.MathConstants import _M_PI
import math
from scipy.optimize import newton

_dist = CumulativeNormalDistribution()


def _checkParameters(strike, forward, displacement):
    strike = float(strike)
    forward = float(forward)
    displacement = float(displacement)
    assert displacement >= 0, "displacement ({0:f}) must be non-negative".format(displacement)
    assert strike + displacement >= 0, "strike + displacement ({0:f}) must be non-negative".format(strike + displacement)
    assert forward + displacement >= 0, "forward + displacement ({0:f}) must be non-negative".format(forward + displacement)
    return strike, forward, displacement


def blackFormula(optionType,
                 strike,
                 forward,
                 stdev,
                 discount=1.0,
                 displacement=0.0):

    strike, forward, displacement = _checkParameters(strike, forward, displacement)

    if stdev == 0.0:
        return max((forward - strike) * optionType, 0.0) * discount

    forward += displacement
    strike += displacement

    if strike == 0.0:
        return forward * discount if optionType == OptionType.Call else 0.0

    d1 = math.log(forward / strike) / stdev + 0.5 * stdev
    d2 = d1 - stdev
    nd1 = _dist(d1 * optionType)
    nd2 = _dist(d2 * optionType)

    return discount * optionType * (forward * nd1 - strike * nd2)


def _blackFormulaImpliedStdDevApproximation(optionType,
                                            strike,
                                            forward,
                                            blackPrice,
                                            discount=1.0,
                                            displacement=0.0):

    forward += displacement
    strike += displacement

    result0 = blackPrice / discount * math.sqrt(2.0 * _M_PI) / forward

    moneynessDelta = optionType * (forward - strike)
    moneynessDelta_2 = moneynessDelta / 2.0
    temp = blackPrice / discount - moneynessDelta_2
    moneynessDelta_PI = moneynessDelta * moneynessDelta / _M_PI
    temp2 = temp * temp - moneynessDelta_PI

    innerTmp = 0.0
    innerTmp2 = 0.0

    if temp2 < innerTmp:
        temp2 = innerTmp2

    temp2 = math.sqrt(temp2)
    temp += temp2
    temp *= math.sqrt(2.0 * _M_PI)
    result1 = temp / (forward + strike)

    if strike == forward:
        stdDev = result0
    else:
        stdDev = result1
    return stdDev


def blackFormulaImpliedStdDev(optionType,
                              strike,
                              forward,
                              blackPrice,
                              discount=1.0,
                              displacement=0.0):

    otherOptionPrice = blackPrice - optionType * (forward - strike) * discount
    if optionType == OptionType.Put and strike > forward:
        optionType = OptionType.Call
        blackPrice = otherOptionPrice
    if optionType == OptionType.Call and strike < forward:
        optionType = OptionType.Put
        blackPrice = otherOptionPrice

    strike += displacement
    forward += displacement

    func = lambda x: blackFormula(optionType, strike, forward, x, discount, displacement) - blackPrice

    stdAppr = _blackFormulaImpliedStdDevApproximation(optionType,
                                                      strike,
                                                      forward,
                                                      blackPrice,
                                                      discount,
                                                      displacement)
    assert stdAppr >= 0.0, "stdDev ({0:f})) must be non-negative".format(stdAppr)
    return newton(func, stdAppr, tol=1e-10)





