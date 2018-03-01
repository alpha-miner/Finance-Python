# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

import copy
import bisect
import six
import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport isnan
from libc.math cimport log
from libc.math cimport sqrt
from copy import deepcopy
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Math.Accumulators.IAccumulators cimport Latest
from PyFin.Math.Accumulators.IAccumulators cimport StatelessSingleValueAccumulator
from PyFin.Math.Accumulators.IAccumulators cimport build_holder
from PyFin.Math.Accumulators.StatelessAccumulators cimport PositivePart
from PyFin.Math.Accumulators.StatelessAccumulators cimport NegativePart
from PyFin.Math.Accumulators.StatelessAccumulators cimport XAverage
from PyFin.Math.Accumulators.IAccumulators cimport Pow
from PyFin.Utilities.Asserts cimport pyFinAssert
from PyFin.Utilities.Asserts cimport isClose
from PyFin.Math.Accumulators.impl cimport Deque
from PyFin.Math.MathConstants cimport NAN


cdef _checkParameterList(dependency):
    if not isinstance(dependency, Accumulator) and len(dependency) > 1 and not isinstance(dependency, six.string_types):
        raise ValueError("This value holder (e.g. Max or Minimum) can't hold more than 2 parameter names ({0})"
                         " provided".format(dependency))


cdef class StatefulValueHolder(Accumulator):

    def __init__(self, window, dependency):
        super(StatefulValueHolder, self).__init__(dependency)
        if not isinstance(window, int):
            raise ValueError("window parameter should be a positive int however {0} received"
                             .format(window))
        pyFinAssert(window > 0, ValueError, "window length should be greater than 0")
        self._returnSize = 1
        self._window = window
        self._deque = Deque(window)

    cpdef size_t size(self):
        return self._deque.size()

    cpdef bint isFull(self):
        return self._isFull

    cpdef copy_attributes(self, dict attributes, bint is_deep=True):
        super(StatefulValueHolder, self).copy_attributes(attributes, is_deep)
        self._deque = copy.deepcopy(attributes['_deque']) if is_deep else attributes['_deque']

    cpdef collect_attributes(self):
        attributes = super(StatefulValueHolder, self).collect_attributes()
        attributes['_deque'] = self._deque
        return attributes


cdef class Shift(StatefulValueHolder):

    def __init__(self, valueHolder, N=1):
        super(Shift, self).__init__(N, valueHolder._dependency)
        pyFinAssert(N >= 1, ValueError, "shift value should always not be less than 1")
        self._valueHolder = build_holder(valueHolder)
        self._window = valueHolder.window + N
        self._returnSize = valueHolder.valueSize
        self._dependency = deepcopy(valueHolder.dependency)
        self._popout = NAN

    cpdef push(self, dict data):
        self._valueHolder.push(data)
        self._popout = self._deque.dump(self._valueHolder.result())
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._popout

    cpdef int lag(self):
        return self._window - self._valueHolder.window

    def __str__(self):
        return '\mathrm{{Shift}}({0}, {1})'.format(str(self._valueHolder),
                                                   self._window - self._valueHolder.window)


cdef class SingleValuedValueHolder(StatefulValueHolder):
    def __init__(self, window, dependency):
        super(SingleValuedValueHolder, self).__init__(window, dependency)
        _checkParameterList(dependency)

    cpdef double _push(self, dict data):

        cdef Accumulator comp

        cdef double value
        cdef int isValueHolder = self._isValueHolderContained

        if not isValueHolder and self._dependency in data:
            return data[self._dependency]
        elif isValueHolder:
            comp = self._dependency
            comp.push(data)
            return comp.result()
        else:
            return NAN


cdef class SortedValueHolder(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(SortedValueHolder, self).__init__(window, dependency)
        self._sortedArray = []

    cpdef push(self, dict data):
        cdef double value
        cdef double popout
        cdef int delPos

        value = self._push(data)
        if isnan(value):
            return NAN
        if self._deque.isFull():
            popout = self._deque.dump(value)
            delPos = bisect.bisect_left(self._sortedArray, popout)
            del self._sortedArray[delPos]
            bisect.insort_left(self._sortedArray, value)
        else:
            self._deque.dump(value)
            bisect.insort_left(self._sortedArray, value)
        self._isFull = self._isFull or self._deque.isFull()

    cpdef copy_attributes(self, dict attributes, bint is_deep=True):
        super(SortedValueHolder, self).copy_attributes(attributes, is_deep)
        self._sortedArray = copy.deepcopy(attributes['_sortedArray']) if is_deep else attributes['_sortedArray']

    cpdef collect_attributes(self):
        attributes = super(SortedValueHolder, self).collect_attributes()
        attributes['_sortedArray'] = self._sortedArray
        return attributes


cdef class MovingMax(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMax, self).__init__(window, dependency)

    cpdef object result(self):
        if self._sortedArray:
            return self._sortedArray[-1]
        else:
            return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{MMax}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{MMax}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingMin(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMin, self).__init__(window, dependency)

    cpdef object result(self):
        if self._sortedArray:
            return self._sortedArray[0]
        else:
            return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{MMin}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{MMin}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingQuantile(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingQuantile, self).__init__(window, dependency)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef size_t n = len(self._sortedArray)
        if n > 1:
            return self._sortedArray.index(self._deque[n-1]) / (n - 1.)
        else:
            return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{MQuantile}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{MQuantile}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingAllTrue(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingAllTrue, self).__init__(window, dependency)
        self._countedTrue = 0

    cpdef push(self, dict data):

        cdef double value
        cdef int addedTrue
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return NAN
        addedTrue = 0

        if value:
            addedTrue += 1
        popout = self._deque.dump(value, False)
        if popout:
            addedTrue -= 1

        self._countedTrue += addedTrue
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._countedTrue == self.size()

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{MAllTrue}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{MAllTrue}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingAnyTrue(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingAnyTrue, self).__init__(window, dependency)
        self._countedTrue = 0

    cpdef push(self, dict data):

        cdef double value
        cdef int addedTrue
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return NAN
        addedTrue = 0

        if value:
            addedTrue += 1
        popout = self._deque.dump(value, False)
        if popout:
            addedTrue -= 1

        self._countedTrue += addedTrue
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._countedTrue != 0

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{MAnyTrue}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{MAnyTrue}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingSum(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingSum, self).__init__(window, dependency)
        self._runningSum = 0.0

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)
        self._runningSum = self._runningSum - popout + value

        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._runningSum

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{MSum}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{MSum}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingAverage, self).__init__(window, dependency)
        self._runningSum = 0.0

    cpdef push(self, dict data):

        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)
        self._runningSum += value - popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        cdef size_t size = self.size()
        if size:
            return self._runningSum / size
        else:
            return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{MA}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{MA}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingPositiveAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingPositiveAverage, self).__init__(window, dependency)
        self._runningPositiveSum = 0.0
        self._runningPositiveCount = 0

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return NAN
        popout = self._deque.dump(value, -1.)
        if value > 0.0:
            self._runningPositiveCount += 1
            self._runningPositiveSum += value

        if popout > 0.0:
            self._runningPositiveCount -= 1
            self._runningPositiveSum -= popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        if self._runningPositiveCount == 0:
            return 0.0
        else:
            return self._runningPositiveSum / self._runningPositiveCount

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mposavg}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mposavg}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingPositiveDifferenceAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingPositiveDifferenceAverage, self).__init__(window, dependency)
        runningPositive = PositivePart(build_holder(dependency) - Shift(build_holder(dependency), 1))
        self._runningAverage = MovingAverage(window, dependency=runningPositive)

    cpdef push(self, dict data):
        self._runningAverage.push(data)
        self._isFull = self._isFull or self._runningAverage.isFull()

    cpdef object result(self):
        return self._runningAverage.result()

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mposdiffavg}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mposdiffavg}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingNegativeDifferenceAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingNegativeDifferenceAverage, self).__init__(window, dependency)
        runningNegative = NegativePart(build_holder(dependency) - Shift(build_holder(dependency), 1))
        self._runningAverage = MovingAverage(window, dependency=runningNegative)

    cpdef push(self, dict data):
        self._runningAverage.push(data)
        self._isFull = self._isFull or self._runningAverage.isFull()

    cpdef object result(self):
        return self._runningAverage.result()

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mnegdiffavg}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mnegdiffavg}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingRSI(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingRSI, self).__init__(window, dependency)
        self._posDiffAvg = MovingPositiveDifferenceAverage(window, dependency)
        self._negDiffAvg = MovingNegativeDifferenceAverage(window, dependency)

    cpdef push(self, dict data):
        self._posDiffAvg.push(data)
        self._negDiffAvg.push(data)
        self._isFull = self._isFull or (self._posDiffAvg.isFull() and self._negDiffAvg.isFull())

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double nominator = self._posDiffAvg.result()
        cdef double denominator = nominator - self._negDiffAvg.result()
        if denominator:
            return 100. * nominator / denominator
        else:
            return 50.

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mrsi}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mrsi}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingNegativeAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingNegativeAverage, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 1.)
        if value < 0.0:
            self._runningNegativeCount += 1
            self._runningNegativeSum += value

        if popout < 0.0:
            self._runningNegativeCount -= 1
            self._runningNegativeSum -= popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        if self._runningNegativeCount:
            return self._runningNegativeSum / self._runningNegativeCount
        else:
            return 0.

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mnegavg}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mnegavg}}({0}, ''\\text{{{1}}}'')".format(self._window, str(self._dependency))


cdef class MovingVariance(SingleValuedValueHolder):

    def __init__(self, window, dependency='x', isPopulation=False):
        super(MovingVariance, self).__init__(window, dependency)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling variance can't be calculated with window size < 2")

    cpdef push(self, dict data):

        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)

        self._runningSum += value - popout
        self._runningSumSquare += value * value - popout * popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        cdef size_t length = self._deque.size()
        cdef double tmp

        if length == 0:
            return NAN

        tmp = self._runningSumSquare - self._runningSum * self._runningSum / length

        if self._isPop:
            return tmp / length
        else:
            if length >= 2:
                return tmp / (length - 1)
            else:
                return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mvar}}({0}, {1}, {2})".format(self._window, str(self._dependency), self._isPop)
        else:
            return "\\mathrm{{mvar}}({0}, ''\\text{{{1}}}'', {2})".format(self._window, str(self._dependency), self._isPop)


cdef class MovingStandardDeviation(SingleValuedValueHolder):

    def __init__(self, window, dependency='x', isPopulation=False):
        super(MovingStandardDeviation, self).__init__(window, dependency)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling standard deviation can't be calculated with window size < 2")

    cpdef push(self, dict data):

        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)

        self._runningSum += value - popout
        self._runningSumSquare += value * value - popout * popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        cdef size_t length = self._deque.size()
        cdef double tmp

        if length == 0:
            return NAN

        tmp = self._runningSumSquare - self._runningSum * self._runningSum / length

        if self._isPop:
            return sqrt(tmp / length)
        else:
            if length >= 2:
                return sqrt(tmp / (length - 1))
            else:
                return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mstd}}({0}, {1}, {2})".format(self._window, str(self._dependency), self._isPop)
        else:
            return "\\mathrm{{mstd}}({0}, ''\\text{{{1}}}'', {2})".format(self._window, str(self._dependency), self._isPop)


cdef class MovingNegativeVariance(SingleValuedValueHolder):

    def __init__(self, window, dependency='x', isPopulation=0):
        super(MovingNegativeVariance, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling standard deviation can't be calculated with window size < 2")

    cpdef push(self, dict data):

        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 1.)

        if value < 0:
            self._runningNegativeSum += value
            self._runningNegativeSumSquare += value * value
            self._runningNegativeCount += 1
        if popout < 0:
            self._runningNegativeSum -= popout
            self._runningNegativeSumSquare -= popout * popout
            self._runningNegativeCount -= 1
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):

        cdef int length
        cdef double tmp

        if self._isPop:
            if self._runningNegativeCount >= 1:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / length
            else:
                return NAN
        else:
            if self._runningNegativeCount >= 2:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / (length - 1)
            else:
                return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mnegvar}}({0}, {1}, {2})".format(self._window, str(self._dependency), self._isPop)
        else:
            return "\\mathrm{{mnegvar}}({0}, ''\\text{{{1}}}'', {2})".format(self._window, str(self._dependency), self._isPop)


cdef class MovingCountedPositive(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingCountedPositive, self).__init__(window, dependency)
        self._counts = 0

    cpdef push(self, dict data):

        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, -1.)

        if value > 0:
            self._counts += 1
        if popout > 0:
            self._counts -= 1
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._counts

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mposcount}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mposcount}}({0}, ''\\text{{{1}}}''".format(self._window, str(self._dependency))


cdef class MovingCountedNegative(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingCountedNegative, self).__init__(window, dependency)
        self._counts = 0

    cpdef push(self, dict data):

        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 1)

        if value < 0:
            self._counts += 1
        if popout < 0:
            self._counts -= 1
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._counts

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mnegcount}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mnegcount}}({0}, ''\\text{{{1}}}''".format(self._window, str(self._dependency))


cdef class MovingHistoricalWindow(StatefulValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingHistoricalWindow, self).__init__(window, dependency)
        self._returnSize = window

    cpdef push(self, dict data):

        cdef double value

        value = self.extract(data)
        try:
            if isnan(value):
                return NAN
        except TypeError:
            if not value:
                return NAN
        _ = self._deque.dump(value)
        self._isFull = self._isFull or self._deque.isFull()

    def __getitem__(self, item):
        cdef size_t length = self.size()
        if item >= length:
            raise ValueError("index {0} is out of the bound of the historical current length {1}".format(item, length))

        return self._deque[length - 1 - item]

    cpdef object result(self):
        return [self.__getitem__(i) for i in range(self.size())]


# Calculator for one pair of series
cdef class MovingCorrelation(StatefulValueHolder):

    def __init__(self, window, dependency=('x', 'y')):
        super(MovingCorrelation, self).__init__(window, dependency)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0
        self._default = (0., 0.)

    cpdef push(self, dict data):
        cdef double headLeft
        cdef double headRight

        value = self.extract(data)
        if isnan(value[0]) or isnan(value[1]):
            return NAN
        popout = self._deque.dump(value, self._default)
        headLeft = popout[0]
        headRight = popout[1]

        # updating cached values
        self._runningSumLeft = self._runningSumLeft - headLeft + value[0]
        self._runningSumRight = self._runningSumRight - headRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft - headLeft * headLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight - headRight * headRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare - headLeft * headRight + value[0] * value[1]
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        cdef size_t n = self.size()
        if n >= 2:
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            if not isClose(denominator, 0.):
                denominator = sqrt(denominator)
                return nominator / denominator
            else:
                return 0.0
        else:
            return NAN

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mcorr}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mcorr}}({0}, ''\\text{{{1}}}''".format(self._window, str(self._dependency))


# Calculator for several series
cdef class MovingCorrelationMatrix(StatefulValueHolder):

    def __init__(self, window, dependency='values'):
        super(MovingCorrelationMatrix, self).__init__(window, dependency)
        self._isFirst = 1
        self._runningSum = None
        self._runningSumSquare = None
        self._runningSumCrossSquare = None

    cpdef push(self, dict data):
        values = self.extract(data)
        if isnan(sum(values)):
            return NAN
        if self._isFirst:
            self._runningSum = np.zeros((1, len(values)))
            self._runningSumCrossSquare = np.zeros((len(values), len(values)))
            self._isFirst = 0
        reshapeValues = np.array(values).reshape((1, len(values)))
        popout = self._deque.dump(reshapeValues)
        if not np.any(np.isnan(popout)):
            pyFinAssert(len(values) == self._runningSum.size, ValueError, "size incompatiable")
            self._runningSum += reshapeValues - popout
            self._runningSumCrossSquare += reshapeValues * reshapeValues.T - popout * popout.T
        else:
            pyFinAssert(len(values) == self._runningSum.size, ValueError, "size incompatiable")
            self._runningSum += reshapeValues
            self._runningSumCrossSquare += reshapeValues * reshapeValues.T
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        cdef size_t n = self.size()
        if n >= 2:
            nominator = n * self._runningSumCrossSquare - self._runningSum * self._runningSum.T
            denominator = n * np.diag(self._runningSumCrossSquare) - self._runningSum * self._runningSum
            denominator = np.sqrt(denominator * denominator.T)
            return nominator / denominator
        else:
            return np.ones(len(self._runningSum)) * NAN


cdef class MovingProduct(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingProduct, self).__init__(window, dependency)
        self._runningProduct = 1.0

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return NAN
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningProduct *= value / popout
        else:
            self._runningProduct *= value
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._runningProduct

    def __str__(self):
        if self._isValueHolderContained:
            return "\\mathrm{{mprod}}({0}, {1})".format(self._window, str(self._dependency))
        else:
            return "\\mathrm{{mprod}}({0}, ''\\text{{{1}}}''".format(self._window, str(self._dependency))


cdef class MovingCenterMoment(SingleValuedValueHolder):

    def __init__(self, window, order, dependency='x'):
        super(MovingCenterMoment, self).__init__(window, dependency)
        self._order = order
        self._runningMoment = NAN

    cpdef push(self, dict data):

        cdef double value

        value = self._push(data)
        self._deque.dump(value)
        if isnan(value):
            return NAN
        else:
            self._runningMoment = np.mean(np.power(np.abs(self._deque.as_array() - np.mean(self._deque.as_array())), self._order))
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._runningMoment


cdef class MovingSkewness(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingSkewness, self).__init__(window, dependency)
        runningStd3 = Pow(MovingVariance(window, dependency, isPopulation=1), 1.5)
        runningMoment3 = MovingCenterMoment(window, 3, dependency)
        self._runningSkewness = runningMoment3 / runningStd3

    cpdef push(self, dict data):
        self._runningSkewness.push(data)
        self._isFull = self._isFull or self._runningSkewness.isFull()

    cpdef object result(self):
        return self._runningSkewness.result()


cdef class MovingMaxPos(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMaxPos, self).__init__(window, dependency)
        self._runningTsMaxPos = NAN
        self._max = NAN

    cpdef push(self, dict data):
        super(MovingMaxPos, self).push(data)
        self._max = self._sortedArray[-1]

    cpdef object result(self):
        cdef list tmpList = self._deque.as_list()
        self._runningTsMaxPos = tmpList.index(self._max)
        return self._runningTsMaxPos


cdef class MovingMinPos(SortedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingMinPos, self).__init__(window, dependency)
        self._runningTsMinPos = NAN
        self._min = NAN

    cpdef push(self, dict data):
        super(MovingMinPos, self).push(data)
        self._min = self._sortedArray[0]

    cpdef object result(self):
        cdef list tmpList = self._deque.as_list()
        self._runningTsMinPos = tmpList.index(self._min)
        return self._runningTsMinPos


cdef class MovingKurtosis(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingKurtosis, self).__init__(window, dependency)
        runningStd4 = Pow(MovingVariance(window, dependency, isPopulation=True), 2)
        runningMoment4 = MovingCenterMoment(window, 4, dependency)
        self._runningKurtosis = runningMoment4 / runningStd4

    cpdef push(self, dict data):
        self._runningKurtosis.push(data)
        self._isFull = self._isFull or self._runningKurtosis.isFull()

    cpdef object result(self):
        try:
            return self._runningKurtosis.result()
        except ZeroDivisionError:
                return NAN

cdef class MovingRSV(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingRSV, self).__init__(window, dependency)
        self._cached_value = NAN

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN
        else:
            self._deque.dump(value)
            self._cached_value = value
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        cdef list con = self._deque.as_list()
        return (self._cached_value - min(con)) / (max(con) - min(con))


cdef class MACD(StatelessSingleValueAccumulator):

    def __init__(self, short_win, long_win, dependency='x', method=XAverage):
        super(MACD, self).__init__(dependency)
        self._short_average = method(window=short_win, dependency=dependency)
        self._long_average = method(window=long_win, dependency=dependency)

    cpdef push(self, dict data):
        self._short_average.push(data)
        self._long_average.push(data)
        self._isFull = self._isFull or (self._short_average.isFull() and self._long_average.isFull())

    cpdef object result(self):
        return self._short_average.result() - self._long_average.result()


cdef class MovingRank(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingRank, self).__init__(window, dependency)
        self._runningRank = NAN

    cpdef object result(self):
        self._runningRank = bisect.bisect_left(self._sortedArray, self._deque[self._deque.size() - 1])
        return self._runningRank


# runningJ can be more than 1 or less than 0.
cdef class MovingKDJ(StatefulValueHolder):

    def __init__(self, window, k=3, d=3, dependency='x'):
        super(MovingKDJ, self).__init__(window, dependency)
        self._runningRsv = MovingRSV(window, dependency)
        self._k = k
        self._d = d
        self._runningJ = NAN
        self._runningK = NAN
        self._runningD = NAN

    @cython.cdivision(True)
    cpdef push(self, dict data):
        self._runningRsv.push(data)
        if self._runningRsv.size() == 1:
            self._deque.dump(NAN)
            self._runningJ = NAN
        else:
            rsv = self._runningRsv.value
            self._deque.dump(rsv)
            if self._runningRsv.size() == 2:
                self._runningK = (0.5 * (self._k - 1) + rsv) / self._k
                self._runningD = (0.5 * (self._d - 1) + self._runningK) / self._d
            else:
                self._runningK = (self._runningK * (self._k - 1) + rsv) / self._k
                self._runningD = (self._runningD * (self._d - 1) + self._runningK) / self._d
            self._runningJ = 3 * self._runningK - 2 * self._runningD
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._runningJ


cdef class MovingAroon(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingAroon, self).__init__(window, dependency)

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN
        else:
            self._deque.dump(value)
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        cdef list tmpList = self._deque.as_list()
        cdef double runningAroonOsc = (tmpList.index(np.max(tmpList)) - tmpList.index(np.min(tmpList))) / self.window
        return runningAroonOsc


cdef class MovingBias(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingBias, self).__init__(window, dependency)
        self._runningBias = NAN

    @cython.cdivision(True)
    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return NAN
        else:
            self._deque.dump(value)
            self._runningBias = value / np.mean(self._deque.as_array()) - 1
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._runningBias


cdef class MovingLevel(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingLevel, self).__init__(window, dependency)
        self._runningLevel = 1.

    @cython.cdivision(True)
    cpdef push(self, dict data):
        cdef double value = self._push(data)
        cdef list con
        if isnan(value):
            return NAN
        else:
            self._deque.dump(value)
            if self.size() > 1:
                con = self._deque.as_list()
                self._runningLevel = con[-1] / con[0]
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        return self._runningLevel


cdef class MovingAutoCorrelation(SingleValuedValueHolder):

    def __init__(self, window, lags, dependency='x'):
        super(MovingAutoCorrelation, self).__init__(window, dependency)
        self._lags = lags
        self._runningVecForward = []
        self._runningVecBackward = []
        self._runningAutoCorrMatrix = None
        if window <= lags:
            raise ValueError("lags should be less than window however\n"
                             "window is: {0} while lags is: {1}".format(window, lags))

    cpdef push(self, dict data):
        value = self._push(data)
        if isnan(value):
            return NAN
        else:
            self._deque.dump(value)
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        cdef list tmp_list = self._deque.as_list()
        if len(tmp_list) < self.window:
            return NAN
        else:
            try:
                self._runningVecForward = tmp_list[0:self._window - self._lags]
                self._runningVecBackward = tmp_list[-self._window + self._lags - 1:-1]
                self._runningAutoCorrMatrix = np.cov(self._runningVecBackward, self._runningVecForward) / \
                                              (np.std(self._runningVecBackward) * np.std(self._runningVecForward))
            except ZeroDivisionError:
                return NAN
            return self._runningAutoCorrMatrix[0, 1]

'''
performancer
'''

cdef class MovingLogReturn(SingleValuedValueHolder):

    def __init__(self, window=1, dependency='price'):
        super(MovingLogReturn, self).__init__(window, dependency)
        self._runningReturn = NAN

    @cython.cdivision(True)
    cpdef push(self, dict data):
        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return NAN
        popout = self._deque.dump(value)
        if popout is not NAN and popout != 0.0:
            self._runningReturn = log(value / popout)
        self._isFull = self._isFull or self._deque.isFull()

    cpdef object result(self):
        if self.size() >= self.window:
            return self._runningReturn
        else:
            return NAN


cdef class MovingSharp(StatefulValueHolder):

    def __init__(self, window, dependency=('ret', 'riskFree')):
        super(MovingSharp, self).__init__(window, dependency)
        self._mean = MovingAverage(window, dependency='x')
        self._var = MovingVariance(window, dependency='x', isPopulation=False)

    cpdef push(self, dict data):

        cdef tuple value
        cdef double ret
        cdef double benchmark
        cdef dict new_data

        value = self.extract(data)
        if isnan(value[0]) or isnan(value[1]):
            return NAN
        ret = value[0]
        benchmark = value[1]
        new_data = {'x': ret - benchmark}
        self._mean.push(new_data)
        self._var.push(new_data)
        self._isFull = self._isFull or (self._mean.isFull() and self._var.isFull())

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double tmp = self._var.result()
        if tmp != 0.:
            return self._mean.result() / sqrt(tmp)
        else:
            return NAN


cdef class MovingSortino(StatefulValueHolder):

    def __init__(self, window, dependency=('ret', 'riskFree')):
        super(MovingSortino, self).__init__(window, dependency)
        self._mean = MovingAverage(window, dependency='x')
        self._negativeVar = MovingNegativeVariance(window, dependency='x')

    cpdef push(self, dict data):
        cdef tuple value
        cdef double ret
        cdef double benchmark
        cdef dict new_data

        value = self.extract(data)
        if isnan(value[0]) or isnan(value[1]):
            return NAN
        ret = value[0]
        benchmark = value[1]
        new_data = {'x': ret - benchmark}
        self._mean.push(new_data)
        self._negativeVar.push(new_data)
        self._isFull = self._isFull or (self._negativeVar.isFull() and self._mean.isFull())

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double tmp = self._negativeVar.result()
        if tmp != 0.:
            return self._mean.result() /sqrt(self._negativeVar.result())
        else:
            return NAN


cdef class MovingResidue(StatefulValueHolder):

    def __init__(self, window, x, y):
        super(MovingResidue, self).__init__(window, (x.dependency if isinstance(x, Accumulator) else x,
                                                     y.dependency if isinstance(y, Accumulator) else y))
        self._returnSize = 1
        self._cross = 0.
        self._xsquare = 0.
        self._lasty = NAN
        self._lastx = NAN
        self._x = copy.deepcopy(x) if isinstance(x, Accumulator) else Latest(x)
        self._y = copy.deepcopy(y) if isinstance(y, Accumulator) else Latest(y)
        self._deque_y = Deque(window)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef push(self, dict data):
        cdef double x
        cdef double y
        cdef double head_y
        cdef double head_x

        self._x.push(data)
        x = self._x.result()
        self._y.push(data)
        y = self._y.result()
        if isnan(x) or isnan(y):
            return NAN

        head_x = self._deque.dump(x, 0.)
        head_y = self._deque_y.dump(y, 0.)

        self._cross += x * y - head_x * head_y
        self._xsquare += x * x - head_x * head_x

        self._lastx = x
        self._lasty = y

    cpdef bint isFull(self):
        return self._deque.isFull()

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double coef = self._cross / self._xsquare
        return self._lasty - coef * self._lastx

    def __str__(self):
        return "\\mathrm{{Res}}({0}, {1}, {2})".format(self._window, str(self._x), str(self._y))
