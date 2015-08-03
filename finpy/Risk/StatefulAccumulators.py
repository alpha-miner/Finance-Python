# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import math
import bisect
import numpy as np
from finpy.Risk.IAccumulators import Accumulator


class StatefulValueHolder(Accumulator):

    def __init__(self, window, pNames):
        super(StatefulValueHolder, self).__init__(pNames)
        assert window > 0, "window length should be greater than 0"
        self._returnSize = 1
        self._window = window
        self._dependency = window - 1
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
            popout = 0.0
        else:
            popout = np.zeros(np.shape(value))

        if self.isFull:
            # use list as circular queue
            popout = self._con[self._start]
            self._con[self._start] = value
            self._start = (self._start + 1) % self._window
        elif len(self._con) + 1 == self._window:
            self._con.append(value)
            self._isFull = 1
        else:
            self._con.append(value)
        return popout


class Shift(Accumulator):

    def __init__(self, valueHolder, N=1):
        self._historyContainer = StatefulValueHolder(N, pNames=valueHolder._pNames)
        self._valueHolder = valueHolder

    def push(self, **kwargs):
        self._valueHolder.push(**kwargs)
        self._popout = self._historyContainer._dumpOneValue(self._valueHolder.result())

    def result(self):
        return self._popout

    def shift(self, N=1):
        return Shift(self, N)

class SortedValueHolder(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(SortedValueHolder, self).__init__(window, pNames)
        self._sortedArray = []

    def push(self, **kwargs):
        value = super(SortedValueHolder, self).push(**kwargs)
        if  self.isFull:
            popout = self._dumpOneValue(kwargs[self._pNames])
            delPos = bisect.bisect_left(self._sortedArray, popout)
            del self._sortedArray[delPos]
            bisect.insort_left(self._sortedArray, value)
        else:
            _ = self._dumpOneValue(kwargs[self._pNames])
            bisect.insort_left(self._sortedArray, value)


class MovingMax(SortedValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingMax, self).__init__(window, pNames)

    def result(self):
        return self._sortedArray[-1]


class MovingMinimum(SortedValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingMinimum, self).__init__(window, pNames)

    def result(self):
        return self._sortedArray[0]


class MovingSum(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingSum, self).__init__(window, pNames)
        self._runningSum = 0.0

    def push(self, **kwargs):
        value = super(MovingSum, self).push(**kwargs)
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value

    def result(self):
        return self._runningSum


class MovingAverage(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingAverage, self).__init__(window, pNames)
        self._runningSum = 0.0

    def push(self, **kwargs):
        value = super(MovingAverage, self).push(**kwargs)
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value

    def result(self):
        if self.isFull:
            return self._runningSum / self._window
        else:
            return self._runningSum / self.size


class MovingPositiveAverage(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingPositiveAverage, self).__init__(window, pNames)
        self._runningPositiveSum = 0.0
        self._runningPositiveCount = 0

    def push(self, **kwargs):
        value = super(MovingPositiveAverage, self).push(**kwargs)
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


class MovingNegativeAverage(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingNegativeAverage, self).__init__(window, pNames)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    def push(self, **kwargs):
        value = super(MovingNegativeAverage, self).push(**kwargs)
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


class MovingVariance(StatefulValueHolder):

    def __init__(self, window, pNames='x', isPopulation=False):
        super(MovingVariance, self).__init__(window, pNames)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation
        if not self._isPop:
            assert window >= 2, "sampling variance can't be calculated with window size < 2"

    def push(self, **kwargs):
        value = super(MovingVariance, self).push(**kwargs)
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value
        self._runningSumSquare = self._runningSumSquare - popout * popout + value * value

    def result(self):
        length = self.size
        tmp = self._runningSumSquare - self._runningSum * self._runningSum / length

        if self._isPop:
            return tmp / length
        else:
            if length >= 2:
                return tmp / (length - 1)
            else:
                raise RuntimeError("Container has too few samples: {0:d}".format(self.size))


class MovingNegativeVariance(StatefulValueHolder):

    def __init__(self, window, pNames='x', isPopulation=False):
        super(MovingNegativeVariance, self).__init__(window, pNames)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation

    def push(self, **kwargs):
        value = super(MovingNegativeVariance, self).push(**kwargs)
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
                raise RuntimeError("Negative population variance container has less than 1 samples")
        else:
            if self._runningNegativeCount >= 2:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / (length - 1)
            else:
                raise RuntimeError("Negative sample variance container has less than 2 samples")


class MovingCountedPositive(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingCountedPositive, self).__init__(window, pNames)
        self._counts = 0

    def push(self, **kwargs):
        value = super(MovingCountedPositive, self).push(**kwargs)
        popout = self._dumpOneValue(value)

        if value > 0:
            self._counts += 1
        if popout > 0:
            self._counts -= 1

    def result(self):
        return self._counts


class MovingCountedNegative(StatefulValueHolder):

    def __init__(self, window, pNames='x'):
        super(MovingCountedNegative, self).__init__(window, pNames)
        self._counts = 0

    def push(self, **kwargs):
        value = super(MovingCountedNegative, self).push(**kwargs)
        popout = self._dumpOneValue(value)

        if value < 0:
            self._counts += 1
        if popout < 0:
            self._counts -= 1

    def result(self):
        return self._counts


# Calculator for one pair of series
class MovingCorrelation(StatefulValueHolder):

    def __init__(self, window, pNames=('x', 'y')):
        super(MovingCorrelation, self).__init__(window, pNames)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0

    def push(self, **kwargs):
        value = super(MovingCorrelation, self).push(**kwargs)
        popout = self._dumpOneValue(value)
        headLeft = popout[0]
        headRight = popout[1]

        # updating cached values
        self._runningSumLeft = self._runningSumLeft - headLeft + value[0]
        self._runningSumRight = self._runningSumRight - headRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft - headLeft * headLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight - headRight * headRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare - headLeft * headRight + value[0] * value[1]

    def result(self):

        if self.isFull:
            n = self._window
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          *(n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        elif self.size >= 2:
            n = self.size
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          *(n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        else:
            raise RuntimeError("Container has less than 2 samples")


# Calculator for several series
class MovingCorrelationMatrixVer2(StatefulValueHolder):

    def __init__(self, window, pNames='values'):
        super(MovingCorrelationMatrixVer2, self).__init__(window, pNames)

    def push(self, **kwargs):
        values = super(MovingCorrelationMatrixVer2, self).push(**kwargs)
        _ = self._dumpOneValue(values)

    def result(self):
        if len(self._con) >= 2:
            return np.corrcoef(np.matrix(self._con).T)
        else:
            raise RuntimeError("Container has less than 2 samples")


# Calculator for several series
class MovingCorrelationMatrix(StatefulValueHolder):

    def __init__(self, window, pNames='values'):
        super(MovingCorrelationMatrix, self).__init__(window, pNames)
        self._isFirst = True
        self._runningSum = None
        self._runningSumSquare = None
        self._runningSumCrossSquare = None

    def push(self, **kwargs):
        values = super(MovingCorrelationMatrix, self).push(**kwargs)
        if self._isFirst:
            self._runningSum = np.zeros((1, len(values)))
            self._runningSumCrossSquare = np.zeros((len(values), len(values)))
            self._isFirst = False
        reshapeValues = np.array(values).reshape((1, len(values)))
        popout = self._dumpOneValue(reshapeValues)
        assert len(values) == self._runningSum.size, "size incompatiable"
        self._runningSum += reshapeValues - popout
        self._runningSumCrossSquare += reshapeValues * reshapeValues.T - popout * popout.T

    def result(self):
        if len(self._con) >= 2:
            n = self.size
            nominator = n * self._runningSumCrossSquare - self._runningSum * self._runningSum.T
            denominator = n * np.diag(self._runningSumCrossSquare) - self._runningSum * self._runningSum
            denominator = np.sqrt(denominator * denominator.T)
            return nominator / denominator
        else:
            raise RuntimeError("Container has less than 2 samples")


