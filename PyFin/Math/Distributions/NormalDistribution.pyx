# -*- coding: utf-8 -*-
cimport cython
from PyFin.Math.Distributions.norm cimport pdf
from PyFin.Math.Distributions.norm cimport cdf
from PyFin.Math.Distributions.norm cimport cdf_derivative
from libc.math cimport exp
from libc.math cimport log
from libc.math cimport sqrt
from PyFin.Math.MathConstants cimport M_SQRT_2
from PyFin.Math.MathConstants cimport M_1_SQRTPI
from PyFin.Math.MathConstants cimport QL_EPSILON
from PyFin.Math.MathConstants cimport M_SQRT2
from PyFin.Math.MathConstants cimport M_SQRTPI


cdef double _M_SQRT_2 = M_SQRT_2
cdef double _M_1_SQRTPI = M_1_SQRTPI
cdef double _QL_EPSILON = QL_EPSILON
cdef double _M_SQRT2 = M_SQRT2
cdef double _M_SQRTPI = M_SQRTPI


cdef class NormalDistribution(object):

    cdef double _average
    cdef double _sigma
    cdef double _normalizationFactor
    cdef double _derNormalizationFactor
    cdef double _denominator

    def __init__(self, average=0.0, sigma=1.0):
        self._average = average
        self._sigma = sigma
        self._normalizationFactor = _M_SQRT_2 * _M_1_SQRTPI / self._sigma
        self._derNormalizationFactor = self._sigma * self._sigma
        self._denominator = 2.0 * self._derNormalizationFactor

    @property
    def average(self):
        return self._average

    @property
    def sigma(self):
        return self._sigma

    def __call__(self, double x):
        x = x - self._average
        return pdf(x, self._denominator, self._normalizationFactor)

    @cython.cdivision(True)
    def derivative(self, double x):
        cdef double deltax = x - self._average
        cdef double exponent = -(deltax * deltax) / self._denominator
        cdef double normVal = 0.0 if exponent <= -690.0 else self._normalizationFactor * exp(exponent)
        return -normVal * deltax / self._derNormalizationFactor


    def __deepcopy__(self, memo):
        return NormalDistribution(self._average, self._sigma)

    def __reduce__(self):
        d = {}

        return NormalDistribution, (self._average, self._sigma), d

    def __setstate__(self, state):
        pass

    def __richcmp__(NormalDistribution self, NormalDistribution other, int op):
        if op == 2:
            return self._average == other.average and self._sigma == other.sigma


cdef class CumulativeNormalDistribution(object):

    cdef double _average
    cdef double _sigma

    def __init__(self, average=0.0, sigma=1.0):
        self._average = average
        self._sigma = sigma

    @property
    def average(self):
        return self._average

    @property
    def sigma(self):
        return self._sigma

    @cython.cdivision(True)
    def __call__(self, double z):
        z = (z - self._average) / self._sigma
        return cdf(z)

    @cython.cdivision(True)
    def derivative(self, z):
        cdef double zn = (z - self._average) / self._sigma
        return cdf_derivative(zn) / self._sigma

    def __deepcopy__(self, memo):
        return CumulativeNormalDistribution(self._average, self._sigma)

    def __reduce__(self):
        d = {}

        return CumulativeNormalDistribution, (self._average, self._sigma), d

    def __setstate__(self, state):
        pass

    def __richcmp__(CumulativeNormalDistribution self, CumulativeNormalDistribution other, int op):
        if op == 2:
            return self._average == other.average and self._sigma == other.sigma


cdef double _a1 = -3.969683028665376e+01
cdef double _a2 = 2.209460984245205e+02
cdef double _a3 = -2.759285104469687e+02
cdef double _a4 = 1.383577518672690e+02
cdef double _a5 = -3.066479806614716e+01
cdef double _a6 = 2.506628277459239e+00

cdef double _b1 = -5.447609879822406e+01
cdef double _b2 = 1.615858368580409e+02
cdef double _b3 = -1.556989798598866e+02
cdef double _b4 = 6.680131188771972e+01
cdef double _b5 = -1.328068155288572e+01

cdef double _c1 = -7.784894002430293e-03
cdef double _c2 = -3.223964580411365e-01
cdef double _c3 = -2.400758277161838e+00
cdef double _c4 = -2.549732539343734e+00
cdef double _c5 = 4.374664141464968e+00
cdef double _c6 = 2.938163982698783e+00

cdef double _d1 = 7.784695709041462e-03
cdef double _d2 = 3.224671290700398e-01
cdef double _d3 = 2.445134137142996e+00
cdef double _d4 = 3.754408661907416e+00

# Limits of the approximation regions
cdef double _x_low = 0.02425
cdef double _x_high = 1.0 - _x_low


@cython.cdivision(True)
cdef double _tail_value(double x):
    cdef double z

    if x < _x_low:
        # Rational approximation for the lower region 0<x<u_low
        z = sqrt(-2.0 * log(x))
        z = (((((_c1 * z + _c2) * z + _c3) * z + _c4) * z + _c5) * z + _c6) \
            / ((((_d1 * z + _d2) * z + _d3) * z + _d4) * z + 1.0)
    else:
        # Rational approximation for the upper region u_high<x<1
        z = sqrt(-2.0 * log(1.0 - x))
        z = -(((((_c1 * z + _c2) * z + _c3) * z + _c4) * z + _c5) * z + _c6) \
            / ((((_d1 * z + _d2) * z + _d3) * z + _d4) * z + 1.0)
    return z


cdef class InverseCumulativeNormal(object):

    cdef double _average
    cdef double _sigma
    cdef int _fullAcc

    def __init__(self, average=0.0, sigma=1.0, fullAccuracy=False):
        self._average = average
        self._sigma = sigma
        self._fullAcc = fullAccuracy

    @property
    def average(self):
        return self._average

    @property
    def sigma(self):
        return self._sigma

    @property
    def isFullAcc(self):
        return self._fullAcc

    @cython.cdivision(True)
    cdef double _standard_value(self, double x):

        cdef double z
        cdef double r

        if x < _x_low or x > _x_high:
            z = _tail_value(x)
        else:
            z = x - 0.5
            r = z * z
            z = (((((_a1 * r + _a2) * r + _a3) * r + _a4) * r + _a5) * r + _a6) * z \
                / (((((_b1 * r + _b2) * r + _b3) * r + _b4) * r + _b5) * r + 1.0)
        if self._fullAcc:
            r = (cdf(z) - x) * _M_SQRT2 * _M_SQRTPI * exp(0.5 * z * z)
            z -= r / (1 + 0.5 * z * r)
        return z

    def __call__(self, x):
        return self._average + self._sigma * self._standard_value(x)

    def __deepcopy__(self, memo):
        return InverseCumulativeNormal(self._average, self._sigma, self._fullAcc)

    def __reduce__(self):
        d = {}

        return InverseCumulativeNormal, (self._average, self._sigma, self._fullAcc), d

    def __setstate__(self, state):
        pass

    def __richcmp__(InverseCumulativeNormal self, InverseCumulativeNormal other, int op):
        if op == 2:
            return self._average == other.average and self._sigma == other.sigma and self._fullAcc == self.isFullAcc
