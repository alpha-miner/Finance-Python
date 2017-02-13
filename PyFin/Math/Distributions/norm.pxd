# -*- coding: utf-8 -*-
u"""
Created on 2017-2-4

@author: cheng.li
"""

cimport cython
from libc.math cimport exp


cdef double _M_SQRT_2 = 0.7071067811865475244008443621048490392848359376887
cdef double _M_1_SQRTPI = 0.564189583547756286948


@cython.cdivision(True)
cdef inline double pdf(double x, double denorminator, double normalizer) nogil:
        cdef double exponent = -(x * x) / denorminator
        return 0.0 if exponent <= -690.0 else normalizer * exp(exponent)


cdef double cdf(double z) nogil


cdef inline double cdf_derivative(double z) nogil:
    return pdf(z, 2.0, _M_SQRT_2 * _M_1_SQRTPI)