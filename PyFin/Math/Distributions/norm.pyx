# -*- coding: utf-8 -*-
u"""
Created on 2017-2-4

@author: cheng.li
"""

cimport cython
from libc.math cimport exp
from libc.math cimport fabs
from PyFin.Math.ErrorFunction cimport errorFunction


cdef double _M_SQRT_2 = 0.7071067811865475244008443621048490392848359376887
cdef double _M_1_SQRTPI = 0.564189583547756286948
cdef double _QL_EPSILON = 2.2250738585072014e-308


@cython.cdivision(True)
cdef double pdf(double x, double denorminator, double normalizer):
        cdef double exponent = -(x * x) / denorminator
        return 0.0 if exponent <= -690.0 else normalizer * exp(exponent)


@cython.cdivision(True)
cdef double cdf(double z):
    cdef double sumRes
    cdef double zsqr
    cdef double i
    cdef double g
    cdef double a
    cdef double lasta
    cdef double x
    cdef double y
    cdef double result

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

            if lasta <= a or a < fabs(sumRes * _QL_EPSILON):
                break
        return -pdf(z, 2.0, _M_SQRT_2 * _M_1_SQRTPI) / z * sumRes
    return result


cdef double cdf_derivative(double z):
    return pdf(z, 2.0, _M_SQRT_2 * _M_1_SQRTPI)