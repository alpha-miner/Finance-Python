# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import math
from scipy.optimize import newton
from PyFin.Enums.OptionType import OptionType
from PyFin.Math.Distributions.NormalDistribution import CumulativeNormalDistribution
from PyFin.Math.MathConstants import MathConstants
from PyFin.Utilities import pyFinAssert

_dist = CumulativeNormalDistribution()


def _checkParameters(strike, forward, displacement):
    strike = float(strike)
    forward = float(forward)
    displacement = float(displacement)
    pyFinAssert(displacement >= 0, ValueError, "displacement ({0:f}) must be non-negative".format(displacement))
    pyFinAssert(strike + displacement >= 0, ValueError, "strike + displacement ({0:f}) must be non-negative"
             .format(strike + displacement))
    pyFinAssert(forward + displacement >= 0, ValueError, "forward + displacement ({0:f}) must be non-negative"
             .format(forward + displacement))
    return strike, forward, displacement


def blackFormula(optionType,
                 strike,
                 forward,
                 stdDev,
                 discount=1.0,
                 displacement=0.0):
    strike, forward, displacement = _checkParameters(strike, forward, displacement)

    if stdDev == 0.0:
        return max((forward - strike) * optionType, 0.0) * discount

    forward += displacement
    strike += displacement

    if strike == 0.0:
        return forward * discount if optionType == OptionType.Call else 0.0

    d1 = math.log(forward / strike) / stdDev + 0.5 * stdDev
    d2 = d1 - stdDev
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

    result0 = blackPrice / discount * math.sqrt(2.0 * MathConstants.M_PI) / forward

    moneynessDelta = optionType * (forward - strike)
    moneynessDelta_2 = moneynessDelta / 2.0
    temp = blackPrice / discount - moneynessDelta_2
    moneynessDelta_PI = moneynessDelta * moneynessDelta / MathConstants.M_PI
    temp2 = temp * temp - moneynessDelta_PI

    innerTmp = 0.0
    innerTmp2 = 0.0

    if temp2 < innerTmp:
        temp2 = innerTmp2

    temp2 = math.sqrt(temp2)
    temp += temp2
    temp *= math.sqrt(2.0 * MathConstants.M_PI)
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
    pyFinAssert(stdAppr >= 0.0, ValueError, "stdDev ({0:f})) must be non-negative".format(stdAppr))
    return newton(func, stdAppr, tol=1e-10)


def bachelierFormula(optionType,
                     strike,
                     forward,
                     stdDev,
                     discount=1.0):
    strike = float(strike)
    forward = float(forward)
    stdDev = float(stdDev)
    discount = float(discount)

    pyFinAssert(stdDev >= 0, ValueError, "stdDev ({0:f}) must be non-negative".format(stdDev))
    pyFinAssert(discount > 0, ValueError, "discount ({0:f}) must be positive".format(discount))

    d = (forward - strike) * optionType
    if stdDev == 0:
        return discount * max(d, 0.0)

    h = d / stdDev
    result = discount * (stdDev * _dist.derivative(h) + d * _dist(h))

    pyFinAssert(result >= 0, ValueError, "negative value ({0:f}) for "
                                      "stdDev:  {1:f}"
                                      "option:  {2}"
                                      "strike:  {3:f}"
                                      "forward: {4:f}".format(result, stdDev, optionType, strike, forward))
    return result


def bachelierFormulaImpliedVol(optionType,
                               strike,
                               forward,
                               tte,
                               bachelierPrice,
                               discount=1.0):
    strike = float(strike)
    forward = float(forward)
    tte = float(tte)
    bachelierPrice = float(bachelierPrice)
    discount = float(discount)

    pyFinAssert(tte > 0, ValueError, "tte ({0:f}) must be positive".format(tte))
    SQRT_QL_EPSILON = math.sqrt(MathConstants.QL_EPSILON)

    forwardPremium = bachelierPrice / discount

    if optionType == OptionType.Call:
        straddlePremium = 2.0 * forwardPremium - (forward - strike)
    else:
        straddlePremium = 2.0 * forwardPremium + (forward - strike)

    nu = (forward - strike) / straddlePremium
    nu = max(-1.0 + MathConstants.QL_EPSILON, min(nu, 1.0 - MathConstants.QL_EPSILON))
    eta = 1.0 if (abs(nu) < SQRT_QL_EPSILON) else (nu / math.atanh(nu))

    heta = HCalculator.calculate(eta)
    impliedBpvol = math.sqrt(MathConstants.M_PI / (2 * tte)) * straddlePremium * heta
    return impliedBpvol


# detail implementation


class HCalculator(object):
    _A0 = 3.994961687345134e-1
    _A1 = 2.100960795068497e+1
    _A2 = 4.980340217855084e+1
    _A3 = 5.988761102690991e+2
    _A4 = 1.848489695437094e+3
    _A5 = 6.106322407867059e+3
    _A6 = 2.493415285349361e+4
    _A7 = 1.266458051348246e+4

    _B0 = 1.000000000000000e+0
    _B1 = 4.990534153589422e+1
    _B2 = 3.093573936743112e+1
    _B3 = 1.495105008310999e+3
    _B4 = 1.323614537899738e+3
    _B5 = 1.598919697679745e+4
    _B6 = 2.392008891720782e+4
    _B7 = 3.608817108375034e+3
    _B8 = -2.067719486400926e+2
    _B9 = 1.174240599306013e+1

    @classmethod
    def calculate(cls, eta):
        num = cls._A0 + eta * (cls._A1 + eta * (cls._A2 + eta * (cls._A3 + eta
                                                                 * (cls._A4 + eta * (
            cls._A5 + eta * (cls._A6 + eta * cls._A7))))))

        den = cls._B0 + eta * (cls._B1 + eta * (cls._B2 + eta * (cls._B3 + eta * (cls._B4 + eta
                                                                                  * (cls._B5 + eta * (
            cls._B6 + eta * (cls._B7 + eta * (cls._B8 + eta * cls._B9))))))))

        return math.sqrt(eta) * (num / den)
