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
from PyFin.Math.Accumulators.IAccumulators cimport build_holder
from PyFin.Math.Accumulators.StatelessAccumulators cimport PositivePart
from PyFin.Math.Accumulators.StatelessAccumulators cimport NegativePart
from PyFin.Math.Accumulators.StatelessAccumulators cimport XAverage
from PyFin.Math.Accumulators.IAccumulators cimport Pow
from PyFin.Utilities.Asserts cimport pyFinAssert
from PyFin.Utilities.Asserts cimport isClose
from PyFin.Math.Accumulators.impl cimport Deque
from PyFin.Math.MathConstants cimport NAN


cdef class StatefulValueHolder(Accumulator):

    def __init__(self, window):
        super(StatefulValueHolder, self).__init__()
        if not isinstance(window, int):
            raise ValueError("window parameter should be a positive int however {0} received"
                             .format(window))
        pyFinAssert(window > 0, ValueError, "window length should be greater than 0")
        self._deque = Deque(window)
        self._isFull = False

    cpdef size_t size(self):
        return self._deque.size()

    cpdef bint isFull(self):
        return self._isFull


cdef class Shift(StatefulValueHolder):

    def __init__(self, x, N=1):
        super(Shift, self).__init__(N)
        pyFinAssert(N >= 1, ValueError, "shift value should not be less than 1")
        self._x = build_holder(x)
        self._window = self._x.window + N
        self._dependency = deepcopy(self._x.dependency)
        self._popout = NAN

    cpdef push(self, dict data):
        self._x.push(data)
        self._popout = self._deque.dump(self._x.result())
        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        return self._popout

    cpdef int lag(self):
        return self._window - self._x.window

    def __str__(self):
        return '\mathrm{{Shift}}({0}, {1})'.format(str(self._x), self._window - self._x.window)


cdef class SingleValuedValueHolder(StatefulValueHolder):
    def __init__(self, window, x):
        super(SingleValuedValueHolder, self).__init__(window)
        self._x = build_holder(x)
        self._window = self._x.window + window
        self._dependency = deepcopy(self._x.dependency)


cdef class SortedValueHolder(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(SortedValueHolder, self).__init__(window, x)
        self._sortedArray = []
        self._cur_pos = NAN

    cpdef push(self, dict data):
        cdef double popout
        cdef int delPos

        self._x.push(data)
        cdef double value = self._x.result()
        if isnan(value):
            return NAN
        if self._deque.isFull():
            popout = self._deque.dump(value)
            delPos = bisect.bisect_left(self._sortedArray, popout)
            del self._sortedArray[delPos]
            self._cur_pos = bisect.bisect_left(self._sortedArray, value)
            self._sortedArray.insert(int(self._cur_pos), value)
        else:
            self._deque.dump(value)
            self._cur_pos = bisect.bisect_left(self._sortedArray, value)
            self._sortedArray.insert(int(self._cur_pos), value)
        self._isFull = self._isFull or self._deque.isFull()


cdef class MovingMax(SortedValueHolder):
    def __init__(self, window, x):
        super(MovingMax, self).__init__(window, x)

    cpdef double result(self):
        if self._sortedArray:
            return self._sortedArray[-1]
        else:
            return NAN

    def __str__(self):
        return "\\mathrm{{MMax}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingMin(SortedValueHolder):
    def __init__(self, window, x):
        super(MovingMin, self).__init__(window, x)

    cpdef double result(self):
        if self._sortedArray:
            return self._sortedArray[0]
        else:
            return NAN

    def __str__(self):
        return "\\mathrm{{MMin}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingRank(SortedValueHolder):
    def __init__(self, window, x):
        super(MovingRank, self).__init__(window, x)

    cpdef double result(self):
        return self._cur_pos

    def __str__(self):
        return "\\mathrm{{MRank}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingQuantile(SortedValueHolder):
    def __init__(self, window, x):
        super(MovingQuantile, self).__init__(window, x)

    @cython.cdivision(True)
    cpdef double result(self):
        cdef size_t n = len(self._sortedArray)
        if n > 1:
            return self._cur_pos / (n - 1)
        else:
            return NAN

    def __str__(self):
        return "\\mathrm{{MQuantile}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingAllTrue(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingAllTrue, self).__init__(window, x)
        self._countedTrue = 0

    cpdef push(self, dict data):
        cdef int addedTrue
        cdef double popout

        self._x.push(data)
        cdef double value = self._x.result()
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

    cpdef double result(self):
        return self._countedTrue == self.size()

    def __str__(self):
        return "\\mathrm{{MAllTrue}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingAnyTrue(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingAnyTrue, self).__init__(window, x)
        self._countedTrue = 0

    cpdef push(self, dict data):
        cdef int addedTrue
        cdef double popout

        self._x.push(data)
        cdef double value = self._x.result()
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

    cpdef double result(self):
        return self._countedTrue != 0

    def __str__(self):
        return "\\mathrm{{MAnyTrue}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingSum(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingSum, self).__init__(window, x)
        self._runningSum = 0.0

    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()
        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)
        self._runningSum = self._runningSum - popout + value

        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        return self._runningSum

    def __str__(self):
        return "\\mathrm{{MSum}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingAverage(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingAverage, self).__init__(window, x)
        self._runningSum = 0.0

    cpdef push(self, dict data):
        cdef double popout

        self._x.push(data)
        cdef double value = self._x.result()

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)
        self._runningSum += value - popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef double result(self):
        cdef size_t size = self.size()
        if size:
            return self._runningSum / size
        else:
            return NAN

    def __str__(self):
        return "\\mathrm{{MA}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingPositiveAverage(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingPositiveAverage, self).__init__(window, x)
        self._runningPositiveSum = 0.0
        self._runningPositiveCount = 0

    cpdef push(self, dict data):
        cdef double popout

        self._x.push(data)
        cdef double value = self._x.result()

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
    cpdef double result(self):
        if self._runningPositiveCount == 0:
            return 0.0
        else:
            return self._runningPositiveSum / self._runningPositiveCount

    def __str__(self):
        return "\\mathrm{{mposavg}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingPositiveDifferenceAverage(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingPositiveDifferenceAverage, self).__init__(window, x)
        cdef Accumulator runningPositive = PositivePart(build_holder(x) - Shift(build_holder(x), 1))
        self._runningAverage = MovingAverage(window, x=runningPositive)

    cpdef push(self, dict data):
        self._runningAverage.push(data)
        self._isFull = self._isFull or self._runningAverage.isFull()

    cpdef double result(self):
        return self._runningAverage.result()

    def __str__(self):
        return "\\mathrm{{mposdiffavg}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingNegativeDifferenceAverage(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingNegativeDifferenceAverage, self).__init__(window, x)
        cdef Accumulator runningNegative = NegativePart(build_holder(x) - Shift(build_holder(x), 1))
        self._runningAverage = MovingAverage(window, x=runningNegative)

    cpdef push(self, dict data):
        self._runningAverage.push(data)
        self._isFull = self._isFull or self._runningAverage.isFull()

    cpdef double result(self):
        return self._runningAverage.result()

    def __str__(self):
        return "\\mathrm{{mnegdiffavg}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingRSI(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingRSI, self).__init__(window, x)
        self._posDiffAvg = MovingPositiveDifferenceAverage(window, x)
        self._negDiffAvg = MovingNegativeDifferenceAverage(window, x)

    cpdef push(self, dict data):
        self._posDiffAvg.push(data)
        self._negDiffAvg.push(data)
        self._isFull = self._isFull or (self._posDiffAvg.isFull() and self._negDiffAvg.isFull())

    @cython.cdivision(True)
    cpdef double result(self):
        cdef double nominator = self._posDiffAvg.result()
        cdef double denominator = nominator - self._negDiffAvg.result()
        if denominator:
            return 100. * nominator / denominator
        else:
            return 50.

    def __str__(self):
        return "\\mathrm{{mrsi}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingNegativeAverage(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingNegativeAverage, self).__init__(window, x)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    cpdef push(self, dict data):
        cdef double popout

        self._x.push(data)
        cdef double value = self._x.result()

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
    cpdef double result(self):
        if self._runningNegativeCount:
            return self._runningNegativeSum / self._runningNegativeCount
        else:
            return 0.

    def __str__(self):
        return "\\mathrm{{mnegavg}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingVariance(SingleValuedValueHolder):

    def __init__(self, window, x, isPopulation=False):
        super(MovingVariance, self).__init__(window, x)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling variance can't be calculated with window size < 2")

    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()
        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)

        self._runningSum += value - popout
        self._runningSumSquare += value * value - popout * popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef double result(self):
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
        return "\\mathrm{{mvar}}({0}, {1}, {2})".format(self._window, str(self._x), self._isPop)


cdef class MovingStandardDeviation(SingleValuedValueHolder):

    def __init__(self, window, x, isPopulation=False):
        super(MovingStandardDeviation, self).__init__(window, x)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling standard deviation can't be calculated with window size < 2")

    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 0.)

        self._runningSum += value - popout
        self._runningSumSquare += value * value - popout * popout
        self._isFull = self._isFull or self._deque.isFull()

    @cython.cdivision(True)
    cpdef double result(self):
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
        return "\\mathrm{{mstd}}({0}, {1}, {2})".format(self._window, str(self._x), self._isPop)


cdef class MovingNegativeVariance(SingleValuedValueHolder):

    def __init__(self, window, x, isPopulation=0):
        super(MovingNegativeVariance, self).__init__(window, x)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling standard deviation can't be calculated with window size < 2")

    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()

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
    cpdef double result(self):

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
        return "\\mathrm{{mnegvar}}({0}, {1}, {2})".format(self._window, str(self._x), self._isPop)


cdef class MovingCountedPositive(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingCountedPositive, self).__init__(window, x)
        self._counts = 0

    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, -1.)

        if value > 0:
            self._counts += 1
        if popout > 0:
            self._counts -= 1
        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        return self._counts

    def __str__(self):
        return "\\mathrm{{mposcount}}({0}, {1})".format(self._window, str(self._x))


cdef class MovingCountedNegative(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingCountedNegative, self).__init__(window, x)
        self._counts = 0

    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()

        if isnan(value):
            return NAN
        popout = self._deque.dump(value, 1)

        if value < 0:
            self._counts += 1
        if popout < 0:
            self._counts -= 1
        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        return self._counts

    def __str__(self):
        return "\\mathrm{{mnegcount}}({0}, {1})".format(self._window, str(self._x))


# Calculator for one pair of series
cdef class MovingCorrelation(StatefulValueHolder):

    def __init__(self, window, x, y):
        super(MovingCorrelation, self).__init__(window)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0
        self._x = build_holder(x)
        self._y = build_holder(y)
        self._window = max(self._x.window + window, self._y.window + window)
        self._dependency = list(set(self._x.dependency + self._y.dependency))
        self._deque_y = Deque(window)

    cpdef push(self, dict data):
        cdef double headLeft
        cdef double headRight

        self._x.push(data)
        cdef double x = self._x.result()

        self._y.push(data)
        cdef double y = self._y.result()

        if isnan(x) or isnan(y):
            return NAN

        headLeft = self._deque.dump(x, 0.)
        headRight = self._deque_y.dump(y, 0.)

        # updating cached values
        self._runningSumLeft = self._runningSumLeft - headLeft + x
        self._runningSumRight = self._runningSumRight - headRight + y
        self._runningSumSquareLeft = self._runningSumSquareLeft - headLeft * headLeft + x * x
        self._runningSumSquareRight = self._runningSumSquareRight - headRight * headRight + y * y
        self._runningSumCrossSquare = self._runningSumCrossSquare - headLeft * headRight + x * y
        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        cdef size_t n = self.size()
        cdef double nominator
        cdef double denominator
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
        return "\\mathrm{{mcorr}}({0}, {1}, {2})".format(self._window, str(self._x), str(self._y))


cdef class MovingProduct(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingProduct, self).__init__(window, x)
        self._runningProduct = 1.0

    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()
        if isnan(value):
            return NAN
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningProduct *= value / popout
        else:
            self._runningProduct *= value
        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        return self._runningProduct

    def __str__(self):
        return "\\mathrm{{mprod}}({0}, {1})".format(self._window, str(self._x))


cdef class MACD(Accumulator):

    def __init__(self, short_win, long_win, x, method=XAverage):
        super(MACD, self).__init__()
        self._short_average = method(window=short_win, x=x)
        self._long_average = method(window=long_win, x=x)
        self._isFull = False
        self._window = max(self._short_average.window, self._long_average.window)
        self._dependency = self._short_average._dependency

    cpdef push(self, dict data):
        self._short_average.push(data)
        self._long_average.push(data)
        self._isFull = self._isFull or (self._short_average.isFull() and self._long_average.isFull())

    cpdef double result(self):
        return self._short_average.result() - self._long_average.result()


'''
performancer
'''

cdef class MovingLogReturn(SingleValuedValueHolder):

    def __init__(self, window, x):
        super(MovingLogReturn, self).__init__(window, x)
        self._runningReturn = NAN

    @cython.cdivision(True)
    cpdef push(self, dict data):
        cdef double popout
        self._x.push(data)
        cdef double value = self._x.result()
        if isnan(value):
            return NAN
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningReturn = log(value / popout)
        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        return self._runningReturn


cdef class MovingSharp(StatefulValueHolder):

    def __init__(self, window, x, y):
        super(MovingSharp, self).__init__(window)
        self._mean = MovingAverage(window, x='x')
        self._var = MovingVariance(window, x='x', isPopulation=False)
        self._x = build_holder(x)
        self._y = build_holder(y)
        self._window = max(self._x.window + window, self._y.window + window)
        self._dependency = list(set(self._x.dependency + self._y.dependency))
        self._deque_y = Deque(window)

    cpdef push(self, dict data):

        cdef tuple value
        cdef double ret
        cdef double benchmark
        cdef dict new_data

        self._x.push(data)
        ret = self._x.result()

        self._y.push(data)
        benchmark = self._y.result()

        if isnan(ret) or isnan(benchmark):
            return NAN

        new_data = {'x': ret - benchmark}
        self._mean.push(new_data)
        self._var.push(new_data)
        self._isFull = self._isFull or (self._mean.isFull() and self._var.isFull())

    @cython.cdivision(True)
    cpdef double result(self):
        cdef double tmp = self._var.result()
        if tmp != 0.:
            return self._mean.result() / sqrt(tmp)
        else:
            return NAN


cdef class MovingSortino(StatefulValueHolder):

    def __init__(self, window, x, y):
        super(MovingSortino, self).__init__(window)
        self._mean = MovingAverage(window, x='x')
        self._negativeVar = MovingNegativeVariance(window, x='x')
        self._x = build_holder(x)
        self._y = build_holder(y)
        self._window = max(self._x.window + window, self._y.window + window)
        self._dependency = list(set(self._x.dependency + self._y.dependency))
        self._deque_y = Deque(window)

    cpdef push(self, dict data):
        cdef tuple value
        cdef double ret
        cdef double benchmark
        cdef dict new_data

        self._x.push(data)
        ret = self._x.result()

        self._y.push(data)
        benchmark = self._y.result()

        if isnan(ret) or isnan(benchmark):
            return NAN

        new_data = {'x': ret - benchmark}
        self._mean.push(new_data)
        self._negativeVar.push(new_data)
        self._isFull = self._isFull or (self._negativeVar.isFull() and self._mean.isFull())

    @cython.cdivision(True)
    cpdef double result(self):
        cdef double tmp = self._negativeVar.result()
        if tmp != 0.:
            return self._mean.result() /sqrt(self._negativeVar.result())
        else:
            return NAN


cdef class MovingDrawdown(StatefulValueHolder):

    def __init__(self, window, x):
        super(MovingDrawdown, self).__init__(window)
        self._maxer = MovingMax(window + 1, x='x')
        self._maxer.push(dict(x=0.0))
        self._x = build_holder(x)
        self._runningCum = 0.0
        self._currentMax = NAN

    cpdef push(self, dict data):
        self._x.push(data)
        cdef double ret = self._x.result()

        if isnan(ret):
            return NAN

        self._runningCum += ret
        self._maxer.push(dict(x=self._runningCum))
        self._currentMax = self._maxer.result()
        self._isFull = self._isFull or self._maxer.isFull()

    cpdef double result(self):
        return self._runningCum - self._currentMax


cdef class MovingMaxDrawdown(StatefulValueHolder):

    def __init__(self, window, x):
        super(MovingMaxDrawdown, self).__init__(window)
        self._drawdownCalculator = MovingDrawdown(window, 'x')
        self._minimer = MovingMin(window, 'x')
        self._x = build_holder(x)

    cpdef push(self, dict data):
        self._x.push(data)
        cdef double ret = self._x.result()

        if isnan(ret):
            return NAN

        self._drawdownCalculator.push(dict(x=ret))
        cdef double draw_down = self._drawdownCalculator.result()
        self._minimer.push(dict(x=draw_down))
        self._deque.dump(draw_down)
        self._isFull = self._isFull or self._deque.isFull()

    cpdef double result(self):
        return self._minimer.result()


cdef class MovingResidue(StatefulValueHolder):

    def __init__(self, window, x, y):
        super(MovingResidue, self).__init__(window)
        self._cross = 0.
        self._xsquare = 0.
        self._lasty = NAN
        self._lastx = NAN
        self._x = build_holder(x)
        self._y = build_holder(y)
        self._window = max(self._x.window + window, self._y.window + window)
        self._dependency = list(set(self._x.dependency + self._y.dependency))
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
    cpdef double result(self):
        cdef double coef = self._cross / self._xsquare
        return self._lasty - coef * self._lastx

    def __str__(self):
        return "\\mathrm{{Res}}({0}, {1}, {2})".format(self._window, str(self._x), str(self._y))

