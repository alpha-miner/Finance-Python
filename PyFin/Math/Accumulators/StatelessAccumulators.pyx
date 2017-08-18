# -*- coding: utf-8 -*-
u"""
Created on 2015-7-25

@author: cheng.li
"""

import math
import numpy as np
cimport numpy as np
cimport cython
import six
from libc.math cimport isnan
from libc.math cimport log
from libc.math cimport fmax
from libc.math cimport fmin
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Math.Accumulators.IAccumulators cimport Pow
from PyFin.Math.Accumulators.IAccumulators cimport StatelessSingleValueAccumulator
from PyFin.Math.MathConstants cimport NAN
import bisect


cdef _checkParameterList(dependency):
    if not isinstance(dependency, Accumulator) and len(dependency) > 1 and not isinstance(dependency, six.string_types):
        raise ValueError("This value holder (e.g. Max or Minimum) can't hold more than 2 parameter names ({0})"
                         " provided".format(dependency))


cdef class Diff(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Diff, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._curr = NAN
        self._previous = NAN

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN
        self._isFull = True
        self._previous = self._curr
        self._curr = value

    cpdef object result(self):
        return self._curr - self._previous

    def __deepcopy__(self, memo):
        copied = Diff(self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        copied._curr = self._curr
        copied._previous = self._previous
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        d['_curr'] = self._curr
        d['_previous'] = self._previous
        return Diff, (self._dependency,), d

    def __setstate__(self, state):
        self.copy_attributes(state, is_deep=False)
        self._curr = state['_curr']
        self._previous = state['_previous']


cdef class SimpleReturn(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(SimpleReturn, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = NAN
        self._curr = NAN
        self._previous = NAN

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN
        self._isFull = True
        self._previous = self._curr
        self._curr = value

    @cython.cdivision(True)
    cpdef object result(self):

        cdef double denorm = self._previous
        if denorm:
            return self._curr / denorm - 1.
        else:
            return NAN

    def __deepcopy__(self, memo):
        return SimpleReturn(self._dependency)


cdef class LogReturn(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(LogReturn, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = NAN
        self._curr = NAN
        self._previous = NAN

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN
        self._isFull = True
        self._previous = self._curr
        self._curr = value

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double denorm = self._previous
        if denorm:
            return log(self._curr / denorm)
        else:
            return NAN

    def __deepcopy__(self, memo):
        return LogReturn(self._dependency)


cdef class PositivePart(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(PositivePart, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._pos = NAN
        self._isFull = True

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            self._pos = NAN
        else:
            self._pos = fmax(value, 0.)

    cpdef object result(self):
        return self._pos

    def __deepcopy__(self, memo):
        copied = PositivePart(self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        copied._pos = self._pos
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        d['_pos'] = self._pos
        return PositivePart, (self._dependency,), d

    def __setstate__(self, state):
        self.copy_attributes(state, is_deep=False)
        self._pos = state['_pos']


cdef class NegativePart(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(NegativePart, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._neg = NAN
        self._isFull = False

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            self._neg = NAN
        else:
            self._neg = fmin(value, 0.)
            self._isFull = True

    cpdef object result(self):
        return self._neg

    def __deepcopy__(self, memo):
        copied = NegativePart(self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        copied._neg = self._neg
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        d['_neg'] = self._neg
        return NegativePart, (self._dependency,), d

    def __setstate__(self, state):
        self.copy_attributes(state, is_deep=False)
        self._neg = state['_neg']


cdef class Max(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Max, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMax = -np.inf
        self._returnSize = 1
        self._isFull = False

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN

        self._currentMax = fmax(value, self._currentMax)
        self._isFull = True

    cpdef object result(self):
        return self._currentMax

    def __deepcopy__(self, memo):
        return Max(self._dependency)


cdef class Maximum(StatelessSingleValueAccumulator):

    def __init__(self, dependency=('x', 'y')):
        super(Maximum, self).__init__(dependency)
        self._currentMax = NAN
        self._returnSize = 1
        self._isFull = False

    cpdef push(self, dict data):
        cdef object value = self.extract(data)
        self._currentMax = fmax(value[0], value[1])

    cpdef object result(self):
        return self._currentMax

    def __deepcopy__(self, memo):
        return Maximum(self._dependency)


cdef class Min(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Min, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMin = np.inf
        self._returnSize = 1
        self._isFull = False

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN

        self._currentMin = fmin(value, self._currentMin)
        self._isFull = True

    cpdef object result(self):
        return self._currentMin

    def __deepcopy__(self, memo):
        return Min(self._dependency)


cdef class Minimum(StatelessSingleValueAccumulator):

    def __init__(self, dependency=('x', 'y')):
        super(Minimum, self).__init__(dependency)
        self._currentMin = NAN
        self._returnSize = 1
        self._isFull = False

    cpdef push(self, dict data):
        cdef object value = self.extract(data)
        self._currentMin = fmin(value[0], value[1])

    cpdef object result(self):
        return self._currentMin

    def __deepcopy__(self, memo):
        return Minimum(self._dependency)


cdef class Sum(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Sum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = 0.
        self._returnSize = 1
        self._isFull = False

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN

        self._isFull = True
        self._currentSum += value

    cpdef object result(self):
        return self._currentSum

    def __deepcopy__(self, memo):
        return Sum(self._dependency)


cdef class Average(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Average, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = 0.
        self._currentCount = 0
        self._returnSize = 1
        self._isFull = False

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN

        self._isFull = True
        self._currentCount += 1
        self._currentSum += value

    @cython.cdivision(True)
    cpdef object result(self):
        if self._currentCount:
            return self._currentSum / self._currentCount
        else:
            return NAN

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
            return NAN

        self._isFull = True

        if self._count == 0:
            self._average = value
            self._count += 1
        else:
            self._average += self._exp * (value - self._average)

    cpdef object result(self):
        return self._average

    def __deepcopy__(self, memo):
        copied = XAverage(2.0 / self._exp - 1., self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        copied._average = self._average
        copied._count = self._count
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        d['_average'] = self._average
        d['_count'] = self._count
        return XAverage, (2.0 / self._exp - 1., self._dependency), d

    def __setstate__(self, state):
        self.copy_attributes(state, is_deep=False)
        self._average = state['_average']
        self._count = state['_count']


cdef class Variance(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x', bint isPopulation=0):
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
            return NAN

        self._isFull = True

        self._currentSum += value
        self._currentSumSquare += value * value
        self._currentCount += 1

    @cython.cdivision(True)
    cpdef object result(self):

        cdef double tmp = self._currentSumSquare - self._currentSum * self._currentSum / self._currentCount

        cdef double pop_num = self._currentCount if self._isPop else self._currentCount - 1

        if pop_num:
            return tmp / pop_num
        else:
            return NAN

    def __deepcopy__(self, memo):
        return Variance(self._dependency, self._isPop)


cdef class Product(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Product, self).__init__(dependency)
        self._product = 1.0

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN

        self._isFull = True
        self._product *= value

    cpdef object result(self):
        return self._product

    def __deepcopy__(self, memo):
        return Product(self._dependency)


cdef class CenterMoment(StatelessSingleValueAccumulator):

    def __init__(self, order, dependency='x'):
        super(CenterMoment, self).__init__(dependency)
        self._this_list = []
        self._order = order
        self._moment = NAN

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN

        self._isFull = True

        self._this_list.append(value)
        self._moment = np.mean(np.power(np.abs(np.array(self._this_list) - np.mean(self._this_list)), self._order))

    cpdef object result(self):
        return self._moment

    def __deepcopy__(self, memo):
        return CenterMoment(self._order, self._dependency)


cdef class Skewness(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Skewness, self).__init__(dependency)
        cdef Pow std3 = Pow(Variance(dependency, isPopulation=1), 1.5)
        cdef CenterMoment moment3 = CenterMoment(3, dependency)
        self._skewness = moment3 / std3

    cpdef push(self, dict data):
        self._skewness.push(data)

    cpdef object result(self):
        try:
            return self._skewness.result()
        except ZeroDivisionError:
            return NAN

    def __deepcopy__(self, memo):
        return Skewness(self._dependency)


cdef class Kurtosis(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Kurtosis, self).__init__(dependency)
        cdef Pow std4 = Pow(Variance(dependency, isPopulation=1), 2)
        cdef CenterMoment moment4 = CenterMoment(4, dependency)
        self._kurtosis = moment4 / std4

    cpdef push(self, dict data):
        self._kurtosis.push(data)

    cpdef object result(self):
        try:
            return self._kurtosis.result()
        except ZeroDivisionError:
            return NAN

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
            return NAN

        self._isFull = True

        self._thisList.append(value)
        self._sortedList = sorted(self._thisList)

    cpdef object result(self):
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
            return NAN

        self._isFull = True

        self._thisList.append(value)
        if len(self._thisList) == 1:
            self._levelList.append(1.0)
        else:
            self._levelList.append(self._thisList[-1] / self._thisList[0])

    cpdef object result(self):
        return self._levelList

    def __deepcopy__(self, memo):
        return LevelList(self._dependency)


cdef class LevelValue(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(LevelValue, self).__init__(dependency)
        self._thisList = []
        self._levelValue = NAN

    cpdef push(self, dict data):
        value = self._push(data)
        if isnan(value):
            return NAN

        self._isFull = True

        self._thisList.append(value)
        if len(self._thisList) == 1:
            self._levelValue = 1.0
        else:
            self._levelValue = self._thisList[-1] / self._thisList[0]

    cpdef object result(self):
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
            return NAN

        self._isFull = True
        self._thisList.append(value)

    cpdef object result(self):
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
                return NAN
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
                value = [NAN] * len(self._dependency)
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
            return NAN

        self._isFull = True

        self._runningSumLeft = self._runningSumLeft + value[0]
        self._runningSumRight = self._runningSumRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare + value[0] * value[1]
        self._currentCount += 1

    cpdef object result(self):
        n = self._currentCount
        nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
        denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                      * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
        denominator = math.sqrt(denominator)
        if denominator != 0:
            return nominator / denominator
        else:
            return NAN

    def __deepcopy__(self, memo):
        return Correlation(self._dependency)