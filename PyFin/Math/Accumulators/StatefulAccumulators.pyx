# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

import bisect
import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport isnan
from libc.math cimport log
from libc.math cimport sqrt
from copy import deepcopy
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Math.Accumulators.IAccumulators cimport StatelessSingleValueAccumulator
from PyFin.Math.Accumulators.IAccumulators cimport build_holder
from PyFin.Math.Accumulators.StatelessAccumulators cimport PositivePart
from PyFin.Math.Accumulators.StatelessAccumulators cimport NegativePart
from PyFin.Math.Accumulators.StatelessAccumulators cimport XAverage
from PyFin.Math.Accumulators.IAccumulators cimport Pow
from PyFin.Utilities.Asserts cimport pyFinAssert
from PyFin.Utilities.Asserts cimport isClose
from PyFin.Math.Accumulators.impl cimport Deque


cdef _checkParameterList(dependency):
    if not isinstance(dependency, Accumulator) and len(dependency) > 1 and not isinstance(dependency, str):
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

    cpdef int size(self):
        return self._deque.size()

    cpdef int isFull(self):
        return self._deque.isFull()

    def __deepcopy__(self, memo):
        return StatefulValueHolder(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return StatefulValueHolder, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class Shift(StatefulValueHolder):

    def __init__(self, valueHolder, N=1):
        super(Shift, self).__init__(N, valueHolder._dependency)
        pyFinAssert(N >= 1, ValueError, "shift value should always not be less than 1")
        self._valueHolder = build_holder(valueHolder)
        self._window = valueHolder.window + N
        self._returnSize = valueHolder.valueSize
        self._dependency = deepcopy(valueHolder.dependency)
        self._popout = np.nan

    cpdef push(self, dict data):
        self._valueHolder.push(data)
        self._popout = self._deque.dump(self._valueHolder.result())

    cpdef object result(self):
        return self._popout

    cpdef int lag(self):
        return self._window - self._valueHolder.window

    def __deepcopy__(self, memo):
        return Shift(self._valueHolder, self.lag())

    def __reduce__(self):
        d = {}

        return Shift, (self._valueHolder, self.lag()), d

    def __setstate__(self, state):
        pass



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
            return np.nan

    def __deepcopy__(self, memo):
        return SingleValuedValueHolder(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return SingleValuedValueHolder, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


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
            return np.nan
        if self._deque.isFull():
            popout = self._deque.dump(value)
            delPos = bisect.bisect_left(self._sortedArray, popout)
            del self._sortedArray[delPos]
            bisect.insort_left(self._sortedArray, value)
        else:
            self._deque.dump(value)
            bisect.insort_left(self._sortedArray, value)

    def __deepcopy__(self, memo):
        return SortedValueHolder(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return SortedValueHolder, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingMax(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMax, self).__init__(window, dependency)

    cpdef object result(self):
        if self._sortedArray:
            return self._sortedArray[-1]
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return MovingMax(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingMax, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingMinimum(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMinimum, self).__init__(window, dependency)

    cpdef object result(self):
        if self._sortedArray:
            return self._sortedArray[0]
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return MovingMinimum(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingMinimum, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingQuantile(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingQuantile, self).__init__(window, dependency)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef int n = len(self._sortedArray)
        if n > 1:
            return self._sortedArray.index(self._deque[n-1]) / (n - 1.)
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return MovingQuantile(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingQuantile, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


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
            return np.nan
        addedTrue = 0

        if value:
            addedTrue += 1
        popout = self._deque.dump(value)
        if not isnan(popout) and popout:
            addedTrue -= 1

        self._countedTrue += addedTrue

    cpdef object result(self):
        return self._countedTrue == self.size()

    def __deepcopy__(self, memo):
        return MovingAllTrue(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingAllTrue, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


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
            return np.nan
        addedTrue = 0

        if value:
            addedTrue += 1
        popout = self._deque.dump(value)
        if not isnan(popout) and popout:
            addedTrue -= 1

        self._countedTrue += addedTrue

    cpdef object result(self):
        return self._countedTrue != 0

    def __deepcopy__(self, memo):
        return MovingAnyTrue(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingAnyTrue, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingSum(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingSum, self).__init__(window, dependency)
        self._runningSum = 0.0

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningSum = self._runningSum - popout + value
        else:
            self._runningSum = self._runningSum + value

    cpdef object result(self):
        return self._runningSum

    def __deepcopy__(self, memo):
        return MovingSum(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingSum, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingAverage, self).__init__(window, dependency)
        self._runningSum = 0.0

    cpdef push(self, dict data):

        cdef double value = self._push(data)
        cdef double popout

        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningSum += value - popout
        else:
            self._runningSum += value

    @cython.cdivision(True)
    cpdef object result(self):
        cdef int size = self.size()
        if size:
            return self._runningSum / size
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return MovingAverage(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingAverage, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


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
            return np.nan
        popout = self._deque.dump(value)
        if value > 0.0:
            self._runningPositiveCount += 1
            self._runningPositiveSum += value

        if popout > 0.0:
            self._runningPositiveCount -= 1
            self._runningPositiveSum -= popout

    @cython.cdivision(True)
    cpdef object result(self):
        if self._runningPositiveCount == 0:
            return 0.0
        else:
            return self._runningPositiveSum / self._runningPositiveCount

    def __deepcopy__(self, memo):
        return MovingPositiveAverage(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingPositiveAverage, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingPositiveDifferenceAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingPositiveDifferenceAverage, self).__init__(window, dependency)
        runningPositive = PositivePart(build_holder(dependency) - Shift(build_holder(dependency), 1))
        self._runningAverage = MovingAverage(window, dependency=runningPositive)

    cpdef push(self, dict data):
        self._runningAverage.push(data)
        if self._isFull == 0 and self._runningAverage.isFull() == 1:
            self._isFull = 1

    cpdef object result(self):
        return self._runningAverage.result()

    def __deepcopy__(self, memo):
        return MovingPositiveDifferenceAverage(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingPositiveDifferenceAverage, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingNegativeDifferenceAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingNegativeDifferenceAverage, self).__init__(window, dependency)
        runningNegative = NegativePart(build_holder(dependency) - Shift(build_holder(dependency), 1))
        self._runningAverage = MovingAverage(window, dependency=runningNegative)

    cpdef push(self, dict data):
        self._runningAverage.push(data)
        if self._isFull == 0 and self._runningAverage.isFull():
            self._isFull = 1

    cpdef object result(self):
        return self._runningAverage.result()

    def __deepcopy__(self, memo):
        return MovingNegativeDifferenceAverage(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingNegativeDifferenceAverage, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingRSI(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingRSI, self).__init__(window, dependency)
        self._posDiffAvg = MovingPositiveDifferenceAverage(window, dependency)
        self._negDiffAvg = MovingNegativeDifferenceAverage(window, dependency)

    cpdef push(self, dict data):
        self._posDiffAvg.push(data)
        self._negDiffAvg.push(data)

        if self._isFull == 0 and self._posDiffAvg.isFull() and self._negDiffAvg.isFull():
            self._isFull = 1

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double nominator = self._posDiffAvg.result()
        cdef double denominator = nominator - self._negDiffAvg.result()
        if denominator != 0.:
            return 100. * nominator / denominator
        else:
            return 50.

    def __deepcopy__(self, memo):
        return MovingRSI(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingRSI, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingNegativeAverage(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingNegativeAverage, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    cpdef push(self, dict data):
        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if value < 0.0:
            self._runningNegativeCount += 1
            self._runningNegativeSum += value

        if popout < 0.0:
            self._runningNegativeCount -= 1
            self._runningNegativeSum -= popout

    @cython.cdivision(True)
    cpdef object result(self):
        if self._runningNegativeCount == 0:
            return 0.0
        else:
            return self._runningNegativeSum / self._runningNegativeCount

    def __deepcopy__(self, memo):
        return MovingNegativeAverage(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingNegativeAverage, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingVariance(SingleValuedValueHolder):

    def __init__(self, window, dependency='x', isPopulation=False):
        super(MovingVariance, self).__init__(window, dependency)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling variance can't be calculated with window size < 2")

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningSum += value - popout
            self._runningSumSquare += value * value - popout * popout
        else:
            self._runningSum += value
            self._runningSumSquare += value * value

    @cython.cdivision(True)
    cpdef object result(self):
        cdef int length = self._deque.size()
        cdef double tmp

        if length == 0:
            return np.nan

        tmp = self._runningSumSquare - self._runningSum * self._runningSum / length

        if self._isPop:
            return tmp / length
        else:
            if length >= 2:
                return tmp / (length - 1)
            else:
                return np.nan

    def __deepcopy__(self, memo):
        return MovingVariance(self._window, self._dependency, self._isPop)

    def __reduce__(self):
        d = {}

        return MovingVariance, (self._window, self._dependency, self._isPop), d

    def __setstate__(self, state):
        pass


cdef class MovingStandardDeviation(SingleValuedValueHolder):

    def __init__(self, window, dependency='x', isPopulation=False):
        super(MovingStandardDeviation, self).__init__(window, dependency)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling standard deviation can't be calculated with window size < 2")

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningSum += value - popout
            self._runningSumSquare += value * value - popout * popout
        else:
            self._runningSum += value
            self._runningSumSquare += value * value

    @cython.cdivision(True)
    cpdef object result(self):
        cdef int length = self._deque.size()
        cdef double tmp

        if length == 0:
            return np.nan

        tmp = self._runningSumSquare - self._runningSum * self._runningSum / length

        if self._isPop:
            return sqrt(tmp / length)
        else:
            if length >= 2:
                return sqrt(tmp / (length - 1))
            else:
                return np.nan

    def __deepcopy__(self, memo):
        return MovingStandardDeviation(self._window, self._dependency, self._isPop)

    def __reduce__(self):
        d = {}

        return MovingStandardDeviation, (self._window, self._dependency, self._isPop), d

    def __setstate__(self, state):
        pass


cdef class MovingNegativeVariance(SingleValuedValueHolder):

    def __init__(self, window, dependency='x', isPopulation=0):
        super(MovingNegativeVariance, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if value < 0:
            self._runningNegativeSum += value
            self._runningNegativeSumSquare += value * value
            self._runningNegativeCount += 1
        if popout < 0:
            self._runningNegativeSum -= popout
            self._runningNegativeSumSquare -= popout * popout
            self._runningNegativeCount -= 1

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
                return np.nan
        else:
            if self._runningNegativeCount >= 2:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / (length - 1)
            else:
                return np.nan

    def __deepcopy__(self, memo):
        return MovingNegativeVariance(self._window, self._dependency, self._isPop)

    def __reduce__(self):
        d = {}

        return MovingNegativeVariance, (self._window, self._dependency, self._isPop), d

    def __setstate__(self, state):
        pass


cdef class MovingCountedPositive(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingCountedPositive, self).__init__(window, dependency)
        self._counts = 0

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)

        if value > 0:
            self._counts += 1
        if popout > 0:
            self._counts -= 1

    cpdef object result(self):
        return self._counts

    def __deepcopy__(self, memo):
        return MovingCountedPositive(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingCountedPositive, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingCountedNegative(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingCountedNegative, self).__init__(window, dependency)
        self._counts = 0

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)

        if value < 0:
            self._counts += 1
        if popout < 0:
            self._counts -= 1

    cpdef object result(self):
        return self._counts

    def __deepcopy__(self, memo):
        return MovingCountedNegative(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingCountedNegative, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingHistoricalWindow(StatefulValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingHistoricalWindow, self).__init__(window, dependency)
        self._returnSize = window

    cpdef push(self, dict data):

        cdef double value

        value = self.extract(data)
        try:
            if isnan(value):
                return np.nan
        except TypeError:
            if not value:
                return np.nan
        _ = self._deque.dump(value)

    def __getitem__(self, item):
        cdef int length = self.size()
        if item >= length:
            raise ValueError("index {0} is out of the bound of the historical current length {1}".format(item, length))

        return self._deque[length - 1 - item]

    cpdef object result(self):
        return [self.__getitem__(i) for i in range(self.size())]

    def __deepcopy__(self, memo):
        return MovingHistoricalWindow(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingHistoricalWindow, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


# Calculator for one pair of series
cdef class MovingCorrelation(StatefulValueHolder):

    def __init__(self, window, dependency=('x', 'y')):
        super(MovingCorrelation, self).__init__(window, dependency)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0

    cpdef push(self, dict data):
        value = self.extract(data)
        if isnan(value[0]) or isnan(value[1]):
            return np.nan
        popout = self._deque.dump(value)
        if not isnan(popout[0]):
            headLeft = popout[0]
            headRight = popout[1]

            # updating cached values
            self._runningSumLeft = self._runningSumLeft - headLeft + value[0]
            self._runningSumRight = self._runningSumRight - headRight + value[1]
            self._runningSumSquareLeft = self._runningSumSquareLeft - headLeft * headLeft + value[0] * value[0]
            self._runningSumSquareRight = self._runningSumSquareRight - headRight * headRight + value[1] * value[1]
            self._runningSumCrossSquare = self._runningSumCrossSquare - headLeft * headRight + value[0] * value[1]
        else:
            # updating cached values
            self._runningSumLeft = self._runningSumLeft + value[0]
            self._runningSumRight = self._runningSumRight + value[1]
            self._runningSumSquareLeft = self._runningSumSquareLeft + value[0] * value[0]
            self._runningSumSquareRight = self._runningSumSquareRight + value[1] * value[1]
            self._runningSumCrossSquare = self._runningSumCrossSquare + value[0] * value[1]

    cpdef object result(self):
        cdef int n = self.size()
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
            return np.nan

    def __deepcopy__(self, memo):
        return MovingCorrelation(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingCorrelation, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


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
            return np.nan
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

    cpdef object result(self):
        n = self.size()
        if n >= 2:
            nominator = n * self._runningSumCrossSquare - self._runningSum * self._runningSum.T
            denominator = n * np.diag(self._runningSumCrossSquare) - self._runningSum * self._runningSum
            denominator = np.sqrt(denominator * denominator.T)
            return nominator / denominator
        else:
            return np.ones(len(self._runningSum)) * np.nan

    def __deepcopy__(self, memo):
        return MovingCorrelationMatrix(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingCorrelationMatrix, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingProduct(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingProduct, self).__init__(window, dependency)
        self._runningProduct = 1.0

    cpdef push(self, dict data):

        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if not isnan(popout):
            self._runningProduct *= value / popout
        else:
            self._runningProduct *= value

    cpdef object result(self):
        return self._runningProduct

    def __deepcopy__(self, memo):
        return MovingProduct(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingProduct, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingCenterMoment(SingleValuedValueHolder):

    def __init__(self, window, order, dependency='x'):
        super(MovingCenterMoment, self).__init__(window, dependency)
        self._order = order
        self._runningMoment = np.nan

    cpdef push(self, dict data):

        cdef double value

        value = self._push(data)
        self._deque.dump(value)
        if isnan(value):
            return np.nan
        else:
            self._runningMoment = np.mean(np.power(np.abs(self._deque.as_array() - np.mean(self._deque.as_array())), self._order))

    cpdef object result(self):
        return self._runningMoment

    def __deepcopy__(self, memo):
        return MovingCenterMoment(self._window, self._order, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingCenterMoment, (self._window, self._order, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingSkewness(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingSkewness, self).__init__(window, dependency)
        runningStd3 = Pow(MovingVariance(window, dependency, isPopulation=1), 1.5)
        runningMoment3 = MovingCenterMoment(window, 3, dependency)
        self._runningSkewness = runningMoment3 / runningStd3

    cpdef push(self, dict data):
        self._runningSkewness.push(data)

    cpdef object result(self):
        return self._runningSkewness.result()

    def __deepcopy__(self, memo):
        try:
            return MovingSkewness(self._window, self._dependency)
        except ZeroDivisionError:
            return np.nan

    def __reduce__(self):
        d = {}

        return MovingSkewness, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingMaxPos(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMaxPos, self).__init__(window, dependency)
        self._runningTsMaxPos = np.nan
        self._max = np.nan

    cpdef push(self, dict data):
        super(MovingMaxPos, self).push(data)
        self._max = self._sortedArray[-1]

    cpdef object result(self):
        cdef list tmpList = self._deque.as_list()
        self._runningTsMaxPos = tmpList.index(self._max)
        return self._runningTsMaxPos

    def __deepcopy__(self, memo):
        return MovingMaxPos(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingMaxPos, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingMinPos(SortedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingMinPos, self).__init__(window, dependency)
        self._runningTsMinPos = np.nan
        self._min = np.nan

    cpdef push(self, dict data):
        super(MovingMinPos, self).push(data)
        self._min = self._sortedArray[0]

    cpdef object result(self):
        cdef list tmpList = self._deque.as_list()
        self._runningTsMinPos = tmpList.index(self._min)
        return self._runningTsMinPos

    def __deepcopy__(self, memo):
        return MovingMinPos(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingMinPos, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingKurtosis(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingKurtosis, self).__init__(window, dependency)
        runningStd4 = Pow(MovingVariance(window, dependency, isPopulation=True), 2)
        runningMoment4 = MovingCenterMoment(window, 4, dependency)
        self._runningKurtosis = runningMoment4 / runningStd4

    cpdef push(self, dict data):
        self._runningKurtosis.push(data)

    cpdef object result(self):
        try:
            return self._runningKurtosis.result()
        except ZeroDivisionError:
                return np.nan

    def __deepcopy__(self, memo):
        return MovingKurtosis(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingKurtosis, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingRSV(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingRSV, self).__init__(window, dependency)
        self._cached_value = np.nan

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan
        else:
            self._deque.dump(value)
            self._cached_value = value

    @cython.cdivision(True)
    cpdef object result(self):
        cdef list con = self._deque.as_list()
        return (self._cached_value - min(con)) / (max(con) - min(con))

    def __deepcopy__(self, memo):
        return MovingRSV(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingRSV, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MACD(StatelessSingleValueAccumulator):

    def __init__(self, short_win, long_win, dependency='x', method=XAverage):
        super(MACD, self).__init__(dependency)
        self._short_average = method(window=short_win, dependency=dependency)
        self._long_average = method(window=long_win, dependency=dependency)

    cpdef push(self, dict data):
        self._short_average.push(data)
        self._long_average.push(data)
        if self._isFull == 0 and self._short_average.isFull() and self._long_average.isFull():
            self._isFull = 1

    cpdef object result(self):
        return self._short_average.result() - self._long_average.result()

    def __deepcopy__(self, memo):
        return MACD(2. / self._short_average._exp - 1., 2. / self._long_average._exp - 1., self._dependency, type(self._short_average))

    def __reduce__(self):
        d = {}

        return MACD, (2. / self._short_average._exp - 1., 2. / self._long_average._exp - 1., self._dependency, type(self._short_average)), d

    def __setstate__(self, state):
        pass


cdef class MovingRank(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingRank, self).__init__(window, dependency)
        self._runningRank = []

    cpdef object result(self):
        self._runningRank = [bisect.bisect_left(self._sortedArray, x) for x in self._deque.as_list()]
        return self._runningRank

    def __deepcopy__(self, memo):
        return MovingRank(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingRank, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


# runningJ can be more than 1 or less than 0.
cdef class MovingKDJ(StatefulValueHolder):

    def __init__(self, window, k=3, d=3, dependency='x'):
        super(MovingKDJ, self).__init__(window, dependency)
        self._runningRsv = MovingRSV(window, dependency)
        self._k = k
        self._d = d
        self._runningJ = np.nan
        self._runningK = np.nan
        self._runningD = np.nan

    @cython.cdivision(True)
    cpdef push(self, dict data):
        self._runningRsv.push(data)
        if self._runningRsv.size() == 1:
            self._deque.dump(np.nan)
            self._runningJ = np.nan
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

    cpdef object result(self):
        return self._runningJ

    def __deepcopy__(self, memo):
        return MovingKDJ(self._window, self._k, self._d, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingKDJ, (self._window, self._k, self._d, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingAroon(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingAroon, self).__init__(window, dependency)

    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan
        else:
            self._deque.dump(value)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef list tmpList = self._deque.as_list()
        cdef double runningAroonOsc = (tmpList.index(np.max(tmpList)) - tmpList.index(np.min(tmpList))) / self.window
        return runningAroonOsc

    def __deepcopy__(self, memo):
        return MovingAroon(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingAroon, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingBias(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingBias, self).__init__(window, dependency)
        self._runningBias = np.nan

    @cython.cdivision(True)
    cpdef push(self, dict data):
        cdef double value = self._push(data)
        if isnan(value):
            return np.nan
        else:
            self._deque.dump(value)
            self._runningBias = value / np.mean(self._deque.as_array()) - 1

    cpdef object result(self):
        return self._runningBias

    def __deepcopy__(self, memo):
        return MovingBias(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingBias, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingLevel(SingleValuedValueHolder):

    def __init__(self, window, dependency='x'):
        super(MovingLevel, self).__init__(window, dependency)
        self._runningLevel = 1.

    @cython.cdivision(True)
    cpdef push(self, dict data):
        cdef double value = self._push(data)
        cdef list con
        if isnan(value):
            return np.nan
        else:
            self._deque.dump(value)
            if self.size() > 1:
                con = self._deque.as_list()
                self._runningLevel = con[-1] / con[0]

    cpdef object result(self):
        return self._runningLevel

    def __deepcopy__(self, memo):
        return MovingLevel(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingLevel, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


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
            return np.nan
        else:
            self._deque.dump(value)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef list tmp_list = self._deque.as_list()
        if len(tmp_list) < self.window:
            return np.nan
        else:
            try:
                self._runningVecForward = tmp_list[0:self._window - self._lags]
                self._runningVecBackward = tmp_list[-self._window + self._lags - 1:-1]
                self._runningAutoCorrMatrix = np.cov(self._runningVecBackward, self._runningVecForward) / \
                                              (np.std(self._runningVecBackward) * np.std(self._runningVecForward))
            except ZeroDivisionError:
                return np.nan
            return self._runningAutoCorrMatrix[0, 1]

    def __deepcopy__(self, memo):
        return MovingAutoCorrelation(self._window, self._lags, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingAutoCorrelation, (self._window, self._lags, self._dependency), d

    def __setstate__(self, state):
        pass

'''
performancer
'''

cdef class MovingLogReturn(SingleValuedValueHolder):

    def __init__(self, window=1, dependency='price'):
        super(MovingLogReturn, self).__init__(window, dependency)
        self._runningReturn = np.nan

    @cython.cdivision(True)
    cpdef push(self, dict data):
        cdef double value
        cdef double popout

        value = self._push(data)
        if isnan(value):
            return np.nan
        popout = self._deque.dump(value)
        if popout is not np.nan and popout != 0.0:
            self._runningReturn = log(value / popout)

    cpdef object result(self):
        if self.size() >= self.window:
            return self._runningReturn
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return MovingLogReturn(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingLogReturn, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingSharp(StatefulValueHolder):

    def __init__(self, window, dependency=('ret', 'riskFree')):
        super(MovingSharp, self).__init__(window, dependency)
        self._mean = MovingAverage(window, dependency='x')
        self._var = MovingVariance(window, dependency='x', isPopulation=False)

    cpdef push(self, dict data):

        cdef tuple value
        cdef double ret
        cdef double benchmark

        value = self.extract(data)
        if isnan(value[0]) or isnan(value[1]):
            return np.nan
        ret = value[0]
        benchmark = value[1]
        data = {'x': ret - benchmark}
        self._mean.push(data)
        self._var.push(data)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double tmp = self._var.result()
        if not isClose(tmp, 0.):
            return self._mean.result() / sqrt(self._var.result())
        else:
            return np.nan

    def __deepcopy__(self, memo):
        return MovingSharp(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingSharp, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingSortino(StatefulValueHolder):

    def __init__(self, window, dependency=('ret', 'riskFree')):
        super(MovingSortino, self).__init__(window, dependency)
        self._mean = MovingAverage(window, dependency='x')
        self._negativeVar = MovingNegativeVariance(window, dependency='x')

    cpdef push(self, dict data):
        cdef tuple value
        cdef double ret
        cdef double benchmark

        value = self.extract(data)
        if isnan(value[0]) or isnan(value[1]):
            return np.nan
        ret = value[0]
        benchmark = value[1]
        data = {'x': ret - benchmark}
        self._mean.push(data)
        self._negativeVar.push(data)

    @cython.cdivision(True)
    cpdef object result(self):
        return self._mean.result() /sqrt(self._negativeVar.result())

    def __deepcopy__(self, memo):
        return MovingSortino(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingSortino, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingAlphaBeta(StatefulValueHolder):

    def __init__(self, window, dependency=('pRet', 'mRet', 'riskFree')):
        super(MovingAlphaBeta, self).__init__(window, dependency)
        self._returnSize = 2
        self._pReturnMean = MovingAverage(window, dependency='x')
        self._mReturnMean = MovingAverage(window, dependency='y')
        self._pReturnVar = MovingVariance(window, dependency='x')
        self._mReturnVar = MovingVariance(window, dependency='y')
        self._correlationHolder = MovingCorrelation(window, dependency=['x', 'y'])

    cpdef push(self, dict data):

        cdef double pReturn
        cdef double mReturn
        cdef double rf

        value = self.extract(data)
        if isnan(value[0]) or isnan(value[1]) or isnan(value[2]):
            return np.nan
        pReturn = value[0]
        mReturn = value[1]
        rf = value[2]
        data = {'x': pReturn - rf, 'y': mReturn - rf}
        self._pReturnMean.push(data)
        self._mReturnMean.push(data)
        self._pReturnVar.push(data)
        self._mReturnVar.push(data)
        self._correlationHolder.push(data)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double corr
        cdef double tmp
        cdef double pStd
        cdef double mStd
        cdef double beta
        cdef double alpha

        corr = self._correlationHolder.result()
        tmp = self._pReturnVar.result()
        if not isClose(tmp, 0.):
            pStd = sqrt(tmp)
        else:
            pStd = 0.
        tmp = self._mReturnVar.result()
        if not isClose(tmp, 0.):
            mStd = sqrt(tmp)
        else:
            mStd = 0.

        if not isClose(tmp, 0.):
            beta = corr * pStd / mStd
        else:
            beta = 0.
        alpha = self._pReturnMean.result() - beta * self._mReturnMean.result()
        return alpha, beta

    def __deepcopy__(self, memo):
        return MovingAlphaBeta(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingAlphaBeta, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingDrawDown(StatefulValueHolder):

    def __init__(self, window, dependency='ret'):
        super(MovingDrawDown, self).__init__(window, dependency)
        self._returnSize = 3
        self._maxer = MovingMax(window + 1, dependency='x')
        self._maxer.push(dict(x=0.0))
        self._runningCum = 0.0
        self._currentMax = np.nan
        self._highIndex = 0
        self._runningIndex = -1

    cpdef push(self, dict data):

        cdef double value = self.extract(data)

        if isnan(value):
            return np.nan
        self._runningIndex += 1
        self._runningCum += value
        self._maxer.push(dict(x=self._runningCum))
        self._currentMax = self._maxer.result()
        if self._runningCum >= self._currentMax:
            self._highIndex = self._runningIndex

    cpdef object result(self):
        return self._runningCum - self._currentMax, self._runningIndex - self._highIndex, self._highIndex

    def __deepcopy__(self, memo):
        return MovingDrawDown(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingDrawDown, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingAverageDrawdown(StatefulValueHolder):

    def __init__(self, window, dependency='ret'):
        super(MovingAverageDrawdown, self).__init__(window, dependency)
        self._returnSize = 2
        self._drawdownCalculator = MovingDrawDown(window, dependency='ret')
        self._drawdownMean = MovingAverage(window, dependency='drawdown')
        self._durationMean = MovingAverage(window, dependency='duration')

    cpdef push(self, dict data):

        cdef double value
        cdef double drawdown
        cdef double duration

        value = self.extract(data)
        if isnan(value):
            return np.nan
        self._drawdownCalculator.push(dict(ret=value))
        drawdown, duration, _ = self._drawdownCalculator.result()
        self._drawdownMean.push(dict(drawdown=drawdown))
        self._durationMean.push(dict(duration=duration))

    cpdef object result(self):
        return self._drawdownMean.result(), self._durationMean.result()

    def __deepcopy__(self, memo):
        return MovingAverageDrawdown(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingAverageDrawdown, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass


cdef class MovingMaxDrawdown(StatefulValueHolder):

    def __init__(self, window, dependency='ret'):
        super(MovingMaxDrawdown, self).__init__(window, dependency)
        self._returnSize = 2
        self._drawdownCalculator = MovingDrawDown(window, 'x')

    cpdef push(self, dict data):
        cdef double value
        cdef double drawdown
        cdef double duration
        cdef int lastHighIndex

        value = self.extract(data)
        if isnan(value):
            return np.nan
        self._drawdownCalculator.push(dict(x=value))
        drawdown, duration, lastHighIndex = self._drawdownCalculator.result()
        self._deque.dump((drawdown, duration, lastHighIndex))

    cpdef object result(self):
        cdef np.ndarray[double, ndim=1] values = np.array([self._deque[i][0] for i in range(self.size())])
        return self._deque[values.argmin()]

    def __deepcopy__(self, memo):
        return MovingMaxDrawdown(self._window, self._dependency)

    def __reduce__(self):
        d = {}

        return MovingMaxDrawdown, (self._window, self._dependency), d

    def __setstate__(self, state):
        pass
