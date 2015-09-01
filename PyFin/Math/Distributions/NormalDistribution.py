# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import math
from PyFin.Math.MathConstants import MathConstants
from PyFin.Math.ErrorFunction import errorFunction

_M_SQRT_2 = MathConstants.M_SQRT_2
_M_1_SQRTPI = MathConstants.M_1_SQRTPI
_QL_EPSILON = MathConstants.QL_EPSILON
_M_SQRT2 = MathConstants.M_SQRT2
_M_SQRTPI = MathConstants.M_SQRTPI


class NormalDistribution(object):
    def __init__(self, average=0.0, sigma=1.0):
        self._average = average
        self._sigma = sigma
        self._normalizationFactor = _M_SQRT_2 * _M_1_SQRTPI / self._sigma
        self._derNormalizationFactor = self._sigma * self._sigma
        self._denominator = 2.0 * self._derNormalizationFactor

    def __call__(self, x):
        deltax = x - self._average
        exponent = -(deltax * deltax) / self._denominator
        return 0.0 if exponent <= -690.0 else self._normalizationFactor * math.exp(exponent)

    def derivative(self, x):
        return (self.__call__(x) * (self._average - x)) / self._derNormalizationFactor


class CumulativeNormalDistribution(object):
    def __init__(self, average=0.0, sigma=1.0):
        self._average = average
        self._sigma = sigma
        self._gaussian = NormalDistribution()

    def __call__(self, z):
        z = (z - self._average) / self._sigma
        result = 0.5 * (1.0 + errorFunction(z * _M_SQRT_2))
        if result <= 1.0e-8:
            sumRes = 1.0
            zsqr = z * z
            i = 1.0
            g = 1.0
            a = 2.20e308
            while True:
                lasta = a
                x = (4.0 * i - 3.0) / zsqr
                y = x * ((4.0 * i - 1.0) / zsqr)
                a = g * (x - y)
                sumRes -= a
                g *= y
                i += 1.0
                if a < 0.0:
                    a = -a

                if lasta <= a or a < math.fabs(sumRes * _QL_EPSILON):
                    break
            return -self._gaussian(z) / z * sumRes
        return result

    def derivative(self, x):
        xn = (x - self._average) / self._sigma
        return self._gaussian(xn) / self._sigma


class InverseCumulativeNormal(object):
    _a1 = -3.969683028665376e+01
    _a2 = 2.209460984245205e+02
    _a3 = -2.759285104469687e+02
    _a4 = 1.383577518672690e+02
    _a5 = -3.066479806614716e+01
    _a6 = 2.506628277459239e+00

    _b1 = -5.447609879822406e+01
    _b2 = 1.615858368580409e+02
    _b3 = -1.556989798598866e+02
    _b4 = 6.680131188771972e+01
    _b5 = -1.328068155288572e+01

    _c1 = -7.784894002430293e-03
    _c2 = -3.223964580411365e-01
    _c3 = -2.400758277161838e+00
    _c4 = -2.549732539343734e+00
    _c5 = 4.374664141464968e+00
    _c6 = 2.938163982698783e+00

    _d1 = 7.784695709041462e-03
    _d2 = 3.224671290700398e-01
    _d3 = 2.445134137142996e+00
    _d4 = 3.754408661907416e+00

    # Limits of the approximation regions
    _x_low = 0.02425
    _x_high = 1.0 - _x_low

    _dist = CumulativeNormalDistribution()

    def __init__(self, average=0.0, sigma=1.0, fullAccuracy=False):
        self._average = average
        self._sigma = sigma
        self._fullAcc = fullAccuracy

    @classmethod
    def _tail_value(cls, x):
        if x <= 0.0 or x >= 1.0:
            raise ArithmeticError("InverseCumulativeNormal({0:f}) undefined: must be 0 < x < 1".format(x))

        if x < cls._x_low:
            # Rational approximation for the lower region 0<x<u_low
            z = math.sqrt(-2.0 * math.log(x))
            z = (((((cls._c1 * z + cls._c2) * z + cls._c3) * z + cls._c4) * z + cls._c5) * z + cls._c6) \
                / ((((cls._d1 * z + cls._d2) * z + cls._d3) * z + cls._d4) * z + 1.0)
        else:
            # Rational approximation for the upper region u_high<x<1
            z = math.sqrt(-2.0 * math.log(1.0 - x))
            z = -(((((cls._c1 * z + cls._c2) * z + cls._c3) * z + cls._c4) * z + cls._c5) * z + cls._c6) \
                / ((((cls._d1 * z + cls._d2) * z + cls._d3) * z + cls._d4) * z + 1.0)
        return z

    def _standard_value(self, x):
        if x < self._x_low or x > self._x_high:
            z = self._tail_value(x)
        else:
            z = x - 0.5
            r = z * z
            z = (((((self._a1 * r + self._a2) * r + self._a3) * r + self._a4) * r + self._a5) * r + self._a6) * z \
                / (((((self._b1 * r + self._b2) * r + self._b3) * r + self._b4) * r + self._b5) * r + 1.0)
        if self._fullAcc:
            r = (self._dist(z) - x) * _M_SQRT2 * _M_SQRTPI * math.exp(0.5 * z * z)
            z -= r / (1 + 0.5 * z * r)
        return z

    def __call__(self, x):
        return self._average + self._sigma * self._standard_value(x)
