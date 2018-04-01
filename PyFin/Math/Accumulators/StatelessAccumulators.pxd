# -*- coding: utf-8 -*-
u"""
Created on 2017-2-10

@author: cheng.li
"""

cimport numpy as np
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator


cdef class Diff(Accumulator):

    cdef public double _curr
    cdef public double _previous
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class SimpleReturn(Accumulator):

    cdef public double _diff
    cdef public double _curr
    cdef public double _previous
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class LogReturn(Accumulator):

    cdef public double _diff
    cdef public double _curr
    cdef public double _previous
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class PositivePart(Accumulator):

    cdef public double _pos
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class NegativePart(Accumulator):

    cdef public double _neg
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Max(Accumulator):

    cdef public double _currentMax
    cdef public int _first
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Maximum(Accumulator):

    cdef public double _currentMax
    cdef Accumulator _x
    cdef Accumulator _y

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Min(Accumulator):

    cdef public double _currentMin
    cdef public int _first
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Minimum(Accumulator):

    cdef public double _currentMin
    cdef public int _first
    cdef Accumulator _x
    cdef Accumulator _y

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Sum(Accumulator):

    cdef public double _currentSum
    cdef public int _first
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Average(Accumulator):

    cdef public double _currentSum
    cdef public int _currentCount
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class XAverage(Accumulator):

    cdef public double _average
    cdef public double _exp
    cdef public int _count
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Variance(Accumulator):

    cdef public double _currentSum
    cdef public double _currentSumSquare
    cdef public int _currentCount
    cdef public bint _isPop
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)


cdef class Product(Accumulator):

    cdef public double _product
    cdef Accumulator _inner

    cpdef push(self, dict data)
    cpdef double result(self)
