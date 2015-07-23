# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import math
from finpy.Math.MathConstants import _M_SQRT_2
from finpy.Math.MathConstants import _M_1_SQRTPI
from finpy.Math.MathConstants import _QL_EPLSON
from finpy.Math.ErrorFunction import errorFunction


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

from numba import jit

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
            a = 0.0
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

                if lasta <= a or a < abs(sumRes * _QL_EPLSON):
                    break
            return -self._gaussian(z) / z * sumRes
        return result


#class InverseCumulativeNormal
