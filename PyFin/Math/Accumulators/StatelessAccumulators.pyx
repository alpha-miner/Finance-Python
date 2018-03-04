# -*- coding: utf-8 -*-
u"""
Created on 2015-7-25

@author: cheng.li
"""

import copy
import math
import numpy as np
cimport numpy as np
cimport cython
import six
from libc.math cimport isnan
from libc.math cimport log
from libc.math cimport fmax
from libc.math cimport fmin
from libc.math cimport sqrt
from PyFin.Math.Accumulators.IAccumulators import build_holder
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Math.Accumulators.IAccumulators cimport Pow
from PyFin.Math.Accumulators.IAccumulators cimport Latest
from PyFin.Math.MathConstants cimport NAN
import bisect


cdef class Diff(Accumulator):

    def __init__(self, x):
        super(Diff, self).__init__()
        self._curr = NAN
        self._previous = NAN
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        cdef double value
        self._inner.push(data)
        value = self._inner.result()
        if isnan(value):
            return NAN
        self._isFull = self._isFull or self._inner.isFull()
        self._previous = self._curr
        self._curr = value

    cpdef double result(self):
        return self._curr - self._previous

    def __str__(self):
        return "\\mathrm{{Diff}}({0})".format(str(self._inner))


cdef class SimpleReturn(Accumulator):

    def __init__(self, x):
        super(SimpleReturn, self).__init__()
        self._diff = NAN
        self._curr = NAN
        self._previous = NAN
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        cdef double value
        self._inner.push(data)
        value = self._inner.result()
        if isnan(value):
            return NAN
        self._isFull = self._isFull or self._inner.isFull()
        self._previous = self._curr
        self._curr = value

    @cython.cdivision(True)
    cpdef double result(self):
        cdef double denorm = self._previous
        if denorm:
            return self._curr / denorm - 1.
        else:
            return NAN


cdef class LogReturn(Accumulator):

    def __init__(self, x):
        super(LogReturn, self).__init__()
        self._diff = NAN
        self._curr = NAN
        self._previous = NAN
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        cdef double value
        self._inner.push(data)
        value = self._inner.result()
        if isnan(value):
            return NAN
        self._isFull = self._isFull or self._inner.isFull()
        self._previous = self._curr
        self._curr = value

    @cython.cdivision(True)
    cpdef double result(self):
        cdef double denorm = self._previous
        if denorm:
            return log(self._curr / denorm)
        else:
            return NAN


cdef class PositivePart(Accumulator):

    def __init__(self, x):
        super(PositivePart, self).__init__()
        self._pos = NAN
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        cdef double value
        self._inner.push(data)
        value = self._inner.result()
        if isnan(value):
            self._pos = NAN
        else:
            self._pos = fmax(value, 0.)
        self._isFull = self._isFull or self._inner.isFull()

    cpdef double result(self):
        return self._pos


cdef class NegativePart(Accumulator):

    def __init__(self, x):
        super(NegativePart, self).__init__()
        self._neg = NAN
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        cdef double value
        self._inner.push(data)
        value = self._inner.result()
        if isnan(value):
            self._neg = NAN
        else:
            self._neg = fmin(value, 0.)
        self._isFull = self._isFull or self._inner.isFull()

    cpdef double result(self):
        return self._neg


cdef class Max(Accumulator):

    def __init__(self, x):
        super(Max, self).__init__()
        self._currentMax = -np.inf
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        cdef double value
        self._inner.push(data)
        value = self._inner.result()
        if isnan(value):
            return NAN

        self._currentMax = fmax(value, self._currentMax)
        self._isFull = self._isFull or self._inner.isFull()

    cpdef double result(self):
        return self._currentMax

cdef class Maximum(Accumulator):

    def __init__(self, x, y):
        super(Maximum, self).__init__()
        self._currentMax = NAN
        self._isFull = False
        self._x = build_holder(x)
        self._y = build_holder(y)
        self._dependency = list(set(self._x.dependency + self._y.dependency))

    cpdef push(self, dict data):
        self._x.push(data)
        cdef double left = self._x.result()
        self._y.push(data)
        cdef double right = self._y.result()
        self._currentMax = fmax(left, right)
        self._isFull = self._isFull or (self._y.isFull() and self._y.isFull())

    cpdef double result(self):
        return self._currentMax


cdef class Min(Accumulator):

    def __init__(self, x):
        super(Min, self).__init__()
        self._currentMin = np.inf
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        self._inner.push(data)
        cdef double value = self._inner.result()
        if isnan(value):
            return NAN

        self._currentMin = fmin(value, self._currentMin)
        self._isFull = self._isFull or self._inner.isFull()

    cpdef double result(self):
        return self._currentMin


cdef class Minimum(Accumulator):

    def __init__(self, x, y):
        super(Minimum, self).__init__()
        self._currentMin = NAN
        self._isFull = False
        self._x = build_holder(x)
        self._y = build_holder(y)
        self._dependency = list(set(self._x.dependency + self._y.dependency))

    cpdef push(self, dict data):
        self._x.push(data)
        cdef double left = self._x.result()
        self._y.push(data)
        cdef double right = self._y.result()
        self._currentMin = fmin(left, right)
        self._isFull = self._isFull or (self._y.isFull() and self._y.isFull())

    cpdef double result(self):
        return self._currentMin


cdef class Sum(Accumulator):

    def __init__(self, x):
        super(Sum, self).__init__()
        self._currentSum = 0.
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        self._inner.push(data)
        cdef double value = self._inner.result()
        if isnan(value):
            return NAN

        self._currentSum += value
        self._isFull = self._isFull or self._inner.isFull()

    cpdef double result(self):
        return self._currentSum


cdef class Average(Accumulator):

    def __init__(self, x):
        super(Average, self).__init__()
        self._currentSum = 0.
        self._currentCount = 0
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        self._inner.push(data)
        cdef double value = self._inner.result()
        if isnan(value):
            return NAN

        self._currentCount += 1
        self._currentSum += value
        self._isFull = self._isFull or self._inner.isFull()

    @cython.cdivision(True)
    cpdef double result(self):
        if self._currentCount:
            return self._currentSum / self._currentCount
        else:
            return NAN


cdef class XAverage(Accumulator):

    def __init__(self, window, x):
        super(XAverage, self).__init__()
        self._average = 0.0
        self._exp = 2.0 / (window + 1.)
        self._count = 0
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        self._inner.push(data)
        cdef double value = self._inner.result()
        if isnan(value):
            return NAN

        if self._count == 0:
            self._average = value
            self._count += 1
        else:
            self._average += self._exp * (value - self._average)
        self._isFull = self._isFull or self._inner.isFull()

    cpdef double result(self):
        return self._average


cdef class Variance(Accumulator):

    def __init__(self, x, bint isPopulation=0):
        super(Variance, self).__init__()
        self._currentSum = 0.0
        self._currentSumSquare = 0.0
        self._currentCount = 0
        self._isPop = isPopulation
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        self._inner.push(data)
        cdef double value = self._inner.result()
        if isnan(value):
            return NAN

        self._isFull = True

        self._currentSum += value
        self._currentSumSquare += value * value
        self._currentCount += 1
        self._isFull = self._isFull or self._inner.isFull()

    @cython.cdivision(True)
    cpdef double result(self):

        cdef double tmp = self._currentSumSquare - self._currentSum * self._currentSum / self._currentCount
        cdef double pop_num = self._currentCount if self._isPop else self._currentCount - 1

        if pop_num:
            return tmp / pop_num
        else:
            return NAN


cdef class Product(Accumulator):

    def __init__(self, x):
        super(Product, self).__init__()
        self._product = 1.0
        self._isFull = False
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        self._inner.push(data)
        cdef double value = self._inner.result()
        if isnan(value):
            return NAN

        self._product *= value
        self._isFull = self._isFull or self._inner.isFull()

    cpdef double result(self):
        return self._product
