# -*- coding: utf-8 -*-
u"""
Created on 2015-7-25

@author: cheng.li
"""

import math
import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport isnan
from libc.math cimport log
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Math.Accumulators.IAccumulators cimport Pow
from PyFin.Math.Accumulators.IAccumulators cimport StatelessSingleValueAccumulator
import bisect


cdef _checkParameterList(dependency):
    if not isinstance(dependency, Accumulator) and len(dependency) > 1 and not isinstance(dependency, str):
        raise ValueError("This value holder (e.g. Max or Minimum) can't hold more than 2 parameter names ({0})"
                         " provided".format(dependency))


cdef class Diff(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Diff, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = np.nan
        self._curr = np.nan
        self._previous = np.nan

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan
        self._isFull = 1
        self._previous = self._curr
        self._curr = value

    cpdef double result(self):
        return self._curr - self._previous

    def __deepcopy__(self, memo):
        return Diff(self._dependency)


cdef class SimpleReturn(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(SimpleReturn, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = np.nan
        self._curr = np.nan
        self._previous = np.nan

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan
        self._isFull = 1
        self._previous = self._curr
        self._curr = value

    @cython.cdivision(True)
    cpdef double result(self):

        cdef double denorm = self._previous
        if denorm:
            return self._curr / denorm - 1.
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return SimpleReturn(self._dependency)


cdef class LogReturn(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(LogReturn, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = np.nan
        self._curr = np.nan
        self._previous = np.nan

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan
        self._isFull = 1
        self._previous = self._curr
        self._curr = value

    @cython.cdivision(True)
    cpdef double result(self):
        cdef double denorm = self._previous
        if denorm:
            return log(self._curr / denorm)
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return LogReturn(self._dependency)


cdef class PositivePart(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(PositivePart, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._pos = np.nan

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        if value > 0.:
            self._pos = value
        elif value <= 0.:
            self._pos = 0.
        else:
            self._pos = np.nan

    cpdef double result(self):
        return self._pos

    def __deepcopy__(self, memo):
        return PositivePart(self._dependency)


cdef class NegativePart(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(NegativePart, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._neg = np.nan

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        if value < 0.:
            self._neg = value
        elif value >= 0.:
            self._neg = 0.
        else:
            self._neg = np.nan

    cpdef double result(self):
        return self._neg

    def __deepcopy__(self, memo):
        return NegativePart(self._dependency)


cdef class Max(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Max, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMax = np.nan
        self._returnSize = 1
        self._first = 1

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        if self._first:
            self._currentMax = value
            self._first = 0
        else:
            if self._currentMax < value:
                self._currentMax = value

    cpdef double result(self):
        return self._currentMax

    def __deepcopy__(self, memo):
        return Max(self._dependency)


cdef class Minimum(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Minimum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMin = np.nan
        self._returnSize = 1
        self._first = 1

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        if self._first:
            self._currentMin = value
            self._first = 0
        else:
            if self._currentMin > value:
                self._currentMin = value

    cpdef double result(self):
        return self._currentMin

    def __deepcopy__(self, memo):
        return Minimum(self._dependency)


cdef class Sum(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Sum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = np.nan
        self._returnSize = 1
        self._first = 1

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        if self._first:
            self._currentSum = value
            self._first = 0
        else:
            self._currentSum += value

    cpdef double result(self):
        return self._currentSum

    def __deepcopy__(self, memo):
        return Sum(self._dependency)


cdef class Average(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Average, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = np.nan
        self._currentCount = 0
        self._returnSize = 1

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        if self._currentCount == 0:
            self._currentSum = value
        else:
            self._currentSum += value
        self._currentCount += 1

    @cython.cdivision(True)
    cpdef double result(self):
        if self._currentCount:
            return self._currentSum / self._currentCount
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return Average(self._dependency)


cdef class XAverage(StatelessSingleValueAccumulator):

    def __init__(self, window, dependency='x'):
        super(XAverage, self).__init__(dependency)
        self._average = 0.0
        self._exp = 2.0 / (window + 1.)
        self._count = 0

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        if self._count == 0:
            self._average = value
        else:
            self._average += self._exp * (value - self._average)
        self._count += 1

    cpdef double result(self):
        return self._average

    def __deepcopy__(self, memo):
        return XAverage(2.0 / self._exp - 1., self._dependency)


cdef class Variance(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x', isPopulation=0):
        super(Variance, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = 0.0
        self._currentSumSquare = 0.0
        self._currentCount = 0
        self._isPop = isPopulation
        self._returnSize = 1

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        self._currentSum += value
        self._currentSumSquare += value * value
        self._currentCount += 1

    @cython.cdivision(True)
    cpdef double result(self):

        cdef double tmp = self._currentSumSquare - self._currentSum * self._currentSum / self._currentCount

        cdef double pop_num = self._currentCount if self._isPop else self._currentCount - 1

        if pop_num:
            return tmp / pop_num
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return Variance(self._dependency, self._isPop)


cdef class Product(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Product, self).__init__(dependency)
        self._product = 1.0

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1
        self._product *= value

    cpdef double result(self):
        return self._product

    def __deepcopy__(self, memo):
        return Product(self._dependency)


cdef class CenterMoment(StatelessSingleValueAccumulator):

    def __init__(self, order, dependency='x'):
        super(CenterMoment, self).__init__(dependency)
        self._this_list = []
        self._order = order
        self._moment = np.nan

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        self._this_list.append(value)
        self._moment = np.mean(np.power(np.abs(np.array(self._this_list) - np.mean(self._this_list)), self._order))

    cpdef double result(self):
        return self._moment

    def __deepcopy__(self, memo):
        return CenterMoment(self._order, self._dependency)


cdef class Skewness(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Skewness, self).__init__(dependency)
        self._std3 = Pow(Variance(dependency, isPopulation=1), 1.5)
        self._moment3 = CenterMoment(3, dependency)
        self._skewness = self._moment3 / self._std3

    cpdef push(self, dict data):
        self._skewness.push(data)

    cpdef double result(self):
        try:
            return self._skewness.result()
        except ZeroDivisionError:
            return np.nan

    def __deepcopy__(self, memo):
        return Skewness(self._dependency)


cdef class Kurtosis(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Kurtosis, self).__init__(dependency)
        self._std4 = Pow(Variance(dependency, isPopulation=1), 2)
        self._moment4 = CenterMoment(4, dependency)
        self._kurtosis = self._moment4 / self._std4

    cpdef push(self, dict data):
        self._kurtosis.push(data)

    cpdef double result(self):
        try:
            return self._kurtosis.result()
        except ZeroDivisionError:
            return np.nan

    def __deepcopy__(self, memo):
        return Kurtosis(self._dependency)


cdef class Rank(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Rank, self).__init__(dependency)
        self._thisList = []
        self._sortedList = []
        self._rank = []

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        self._thisList.append(value)
        self._sortedList = sorted(self._thisList)

    cpdef result(self):
        self._rank = [bisect.bisect_left(self._sortedList, x) for x in self._thisList]
        return self._rank

    def __deepcopy__(self, memo):
        return Rank(self._dependency)


cdef class LevelList(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x', ):
        super(LevelList, self).__init__(dependency)
        self._levelList = []
        self._thisList = []

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        self._thisList.append(value)
        if len(self._thisList) == 1:
            self._levelList.append(1.0)
        else:
            self._levelList.append(self._thisList[-1] / self._thisList[0])

    cpdef result(self):
        return self._levelList

    def __deepcopy__(self, memo):
        return LevelList(self._dependency)


cdef class LevelValue(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(LevelValue, self).__init__(dependency)
        self._thisList = []
        self._levelValue = np.nan

    cpdef push(self, dict data):
        value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1

        self._thisList.append(value)
        if len(self._thisList) == 1:
            self._levelValue = 1.0
        else:
            self._levelValue = self._thisList[-1] / self._thisList[0]

    cpdef double result(self):
        return self._levelValue

    def __deepcopy__(self, memo):
        return LevelValue(self._dependency)


cdef class AutoCorrelation(StatelessSingleValueAccumulator):

    def __init__(self, lags, dependency='x'):
        super(AutoCorrelation, self).__init__(dependency)
        self._lags = lags
        self._thisList = []
        self._VecForward = []
        self._VecBackward = []
        self._AutoCorrMatrix = None

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan

        self._isFull = 1
        self._thisList.append(value)

    cpdef double result(self):
        if len(self._thisList) <= self._lags:
            raise ValueError ("time-series length should be more than lags however\n"
                              "time-series length is: {0} while lags is: {1}".format(len(self._thisList), self._lags))
        else:
            try:
                self._VecForward = self._thisList[0:len(self._thisList) - self._lags]
                self._VecBackward = self._thisList[-len(self._thisList) + self._lags - 1:-1]
                self._AutoCorrMatrix = np.cov(self._VecBackward, self._VecForward) / \
                                (np.std(self._VecBackward) * np.std(self._VecForward))
            except ZeroDivisionError:
                return np.nan
            return self._AutoCorrMatrix[0, 1]

    def __deepcopy__(self, memo):
        return AutoCorrelation(self._lags, self._dependency)


cdef class StatelessMultiValueAccumulator(Accumulator):

    def __init__(self, dependency):
        super(StatelessMultiValueAccumulator, self).__init__(dependency)
        self._returnSize = 1
        self._window = 1

    cdef _push(self, dict data):
        if not self._isValueHolderContained:
            try:
                value = [data[name] for name in self._dependency]
            except KeyError:
                value = [np.nan] * len(self._dependency)
        else:
            self._dependency.push(data)
            value = self._dependency.result()
        return value

    def __deepcopy__(self, memo):
        return StatelessMultiValueAccumulator(self._dependency)


cdef class Correlation(StatelessMultiValueAccumulator):

    def __init__(self, dependency=('x', 'y')):
        super(Correlation, self).__init__(dependency)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0
        self._currentCount = 0
        self._returnSize = 1

    cpdef push(self, dict data):
        value = self._push(data)
        if isnan(value[0]) or isnan(value[1]):
            return np.nan

        self._isFull = 1

        self._runningSumLeft = self._runningSumLeft + value[0]
        self._runningSumRight = self._runningSumRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare + value[0] * value[1]
        self._currentCount += 1

    cpdef double result(self):
        n = self._currentCount
        nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
        denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                      * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
        denominator = math.sqrt(denominator)
        if denominator != 0:
            return nominator / denominator
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return Correlation(self._dependency)