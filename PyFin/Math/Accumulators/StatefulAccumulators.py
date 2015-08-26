# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import math
import bisect
import numpy as np
from copy import deepcopy
from PyFin.Math.Accumulators.IAccumulators import Accumulator
from PyFin.Utilities import pyFinAssert


def _checkParameterList(dependency):
    if not isinstance(dependency, Accumulator) and len(dependency) > 1 and not isinstance(dependency, str):
        raise ValueError("This value holder (e.g. Max or Minimum) can't hold more than 2 parameter names ({0})"
                         " provided".format(dependency))


class StatefulValueHolder(Accumulator):
    def __init__(self, window, dependency):
        super(StatefulValueHolder, self).__init__(dependency)
        if not isinstance(window, int):
            raise ValueError("window parameter should be a positive int however {0} received"
                             .format(window))
        pyFinAssert(window > 0, ValueError, "window length should be greater than 0")
        self._returnSize = 1
        self._window = window
        self._containerSize = window
        self._con = []
        self._isFull = 0
        self._start = 0

    @property
    def isFull(self):
        return self._isFull == 1

    @property
    def size(self):
        return len(self._con)

    def _dumpOneValue(self, value):
        if not hasattr(value, '__iter__'):
            popout = np.nan
        else:
            popout = np.array([np.nan] * len(value))

        if self.isFull:
            # use list as circular queue
            popout = self._con[self._start]
            self._con[self._start] = value
            self._start = (self._start + 1) % self._containerSize
        elif len(self._con) + 1 == self._containerSize:
            self._con.append(value)
            self._isFull = 1
        else:
            self._con.append(value)
        return popout


class Shift(StatefulValueHolder):
    def __init__(self, valueHolder, N=1):
        super(Shift, self).__init__(N, valueHolder._dependency)
        pyFinAssert(N >= 1, ValueError, "shift value should always not be less than 1")
        self._valueHolder = deepcopy(valueHolder)
        self._window = valueHolder.window + N
        self._containerSize = N
        self._returnSize = valueHolder.valueSize
        self._dependency = deepcopy(valueHolder.dependency)

    def push(self, data):
        self._valueHolder.push(data)
        self._popout = super(Shift, self)._dumpOneValue(self._valueHolder.result())

    def result(self):
        return self._popout


class SingleValuedValueHolder(StatefulValueHolder):
    def __init__(self, window, dependency):
        super(SingleValuedValueHolder, self).__init__(window, dependency)
        _checkParameterList(dependency)


class SortedValueHolder(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(SortedValueHolder, self).__init__(window, dependency)
        self._sortedArray = []

    def push(self, data):
        value = super(SortedValueHolder, self).push(data)
        if value is None:
            return
        if self.isFull:
            popout = self._dumpOneValue(value)
            delPos = bisect.bisect_left(self._sortedArray, popout)
            del self._sortedArray[delPos]
            bisect.insort_left(self._sortedArray, value)
        else:
            _ = self._dumpOneValue(value)
            bisect.insort_left(self._sortedArray, value)


class MovingMax(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMax, self).__init__(window, dependency)

    def result(self):
        if self._sortedArray:
            return self._sortedArray[-1]
        else:
            return np.nan


class MovingMinimum(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMinimum, self).__init__(window, dependency)

    def result(self):
        if self._sortedArray:
            return self._sortedArray[0]
        else:
            return np.nan

class MovingSum(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingSum, self).__init__(window, dependency)
        self._runningSum = 0.0

    def push(self, data):
        value = super(MovingSum, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if popout is not np.nan:
            self._runningSum = self._runningSum - popout + value
        else:
            self._runningSum = self._runningSum + value

    def result(self):
        return self._runningSum


class MovingAverage(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingAverage, self).__init__(window, dependency)
        self._runningSum = 0.0

    def push(self, data):
        value = super(MovingAverage, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if popout is not np.nan:
            self._runningSum = self._runningSum - popout + value
        else:
            self._runningSum = self._runningSum + value

    def result(self):
        return self._runningSum / self.size


class MovingPositiveAverage(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingPositiveAverage, self).__init__(window, dependency)
        self._runningPositiveSum = 0.0
        self._runningPositiveCount = 0

    def push(self, data):
        value = super(MovingPositiveAverage, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if value > 0.0:
            self._runningPositiveCount += 1
            self._runningPositiveSum += value

        if popout > 0.0:
            self._runningPositiveCount -= 1
            self._runningPositiveSum -= popout

    def result(self):
        if self._runningPositiveCount == 0:
            return 0.0
        else:
            return self._runningPositiveSum / self._runningPositiveCount


class MovingNegativeAverage(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingNegativeAverage, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    def push(self, data):
        value = super(MovingNegativeAverage, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if value < 0.0:
            self._runningNegativeCount += 1
            self._runningNegativeSum += value

        if popout < 0.0:
            self._runningNegativeCount -= 1
            self._runningNegativeSum -= popout

    def result(self):
        if self._runningNegativeCount == 0:
            return 0.0
        else:
            return self._runningNegativeSum / self._runningNegativeCount


class MovingVariance(SingleValuedValueHolder):
    def __init__(self, window, dependency='x', isPopulation=False):
        super(MovingVariance, self).__init__(window, dependency)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            pyFinAssert(window >= 2, ValueError, "sampling variance can't be calculated with window size < 2")

    def push(self, data):
        value = super(MovingVariance, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if popout is not np.nan:
            self._runningSum = self._runningSum - popout + value
            self._runningSumSquare = self._runningSumSquare - popout * popout + value * value
        else:
            self._runningSum = self._runningSum + value
            self._runningSumSquare = self._runningSumSquare + value * value

    def result(self):
        length = self.size
        tmp = self._runningSumSquare - self._runningSum * self._runningSum / length

        if self._isPop:
            return tmp / length
        else:
            if length >= 2:
                return tmp / (length - 1)
            else:
                raise ZeroDivisionError("Container has too few samples: {0:d}".format(self.size))


class MovingNegativeVariance(SingleValuedValueHolder):
    def __init__(self, window, dependency='x', isPopulation=False):
        super(MovingNegativeVariance, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation

    def push(self, data):
        value = super(MovingNegativeVariance, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if value < 0:
            self._runningNegativeSum += value
            self._runningNegativeSumSquare += value * value
            self._runningNegativeCount += 1
        if popout < 0:
            self._runningNegativeSum -= popout
            self._runningNegativeSumSquare -= popout * popout
            self._runningNegativeCount -= 1

    def result(self):
        if self._isPop:
            if self._runningNegativeCount >= 1:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / length
            else:
                raise ZeroDivisionError("Negative population variance container has less than 1 samples")
        else:
            if self._runningNegativeCount >= 2:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / (length - 1)
            else:
                raise ZeroDivisionError("Negative sample variance container has less than 2 samples")


class MovingCountedPositive(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingCountedPositive, self).__init__(window, dependency)
        self._counts = 0

    def push(self, data):
        value = super(MovingCountedPositive, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)

        if value > 0:
            self._counts += 1
        if popout > 0:
            self._counts -= 1

    def result(self):
        return self._counts


class MovingCountedNegative(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingCountedNegative, self).__init__(window, dependency)
        self._counts = 0

    def push(self, data):
        value = super(MovingCountedNegative, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)

        if value < 0:
            self._counts += 1
        if popout < 0:
            self._counts -= 1

    def result(self):
        return self._counts


class MovingHistoricalWindow(StatefulValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingHistoricalWindow, self).__init__(window, dependency)
        self._returnSize = window

    def push(self, data):
        value = super(MovingHistoricalWindow, self).push(data)
        if value is None:
            return
        _ = self._dumpOneValue(value)

    def __getitem__(self, item):
        length = self.size
        if item >= length:
            raise ValueError("index {0} is out of the bound of the historical current length {1}".format(item, length))
        if self._start:
            recentPoint = self._start - 1
        else:
            recentPoint = self._start + length - 1

        offsetPoint = (recentPoint - item + length) % length
        return self._con[offsetPoint]

    def result(self):
        return [self.__getitem__(i) for i in range(self.size)]


# Calculator for one pair of series
class MovingCorrelation(StatefulValueHolder):
    def __init__(self, window, dependency=('x', 'y')):
        super(MovingCorrelation, self).__init__(window, dependency)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0

    def push(self, data):
        value = super(MovingCorrelation, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if not np.isnan(popout[0]):
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

    def result(self):
        n = self.size
        if n >= 2:
            n = self.size
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        else:
            raise ZeroDivisionError("Container has less than 2 samples")


# Calculator for several series
class MovingCorrelationMatrix(StatefulValueHolder):
    def __init__(self, window, dependency='values'):
        super(MovingCorrelationMatrix, self).__init__(window, dependency)
        self._isFirst = True
        self._runningSum = None
        self._runningSumSquare = None
        self._runningSumCrossSquare = None

    def push(self, data):
        values = super(MovingCorrelationMatrix, self).push(data)
        if values is None:
            return
        if self._isFirst:
            self._runningSum = np.zeros((1, len(values)))
            self._runningSumCrossSquare = np.zeros((len(values), len(values)))
            self._isFirst = False
        reshapeValues = np.array(values).reshape((1, len(values)))
        popout = self._dumpOneValue(reshapeValues)
        if not np.any(np.isnan(popout)):
            pyFinAssert(len(values) == self._runningSum.size, ValueError, "size incompatiable")
            self._runningSum += reshapeValues - popout
            self._runningSumCrossSquare += reshapeValues * reshapeValues.T - popout * popout.T
        else:
            pyFinAssert(len(values) == self._runningSum.size, ValueError, "size incompatiable")
            self._runningSum += reshapeValues
            self._runningSumCrossSquare += reshapeValues * reshapeValues.T

    def result(self):
        if len(self._con) >= 2:
            n = self.size
            nominator = n * self._runningSumCrossSquare - self._runningSum * self._runningSum.T
            denominator = n * np.diag(self._runningSumCrossSquare) - self._runningSum * self._runningSum
            denominator = np.sqrt(denominator * denominator.T)
            return nominator / denominator
        else:
            raise ZeroDivisionError("Container has less than 2 samples")
