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
from PyFin.Math.Accumulators.StatelessAccumulators import Latest
from PyFin.Math.Accumulators.StatelessAccumulators import Positive
from PyFin.Math.Accumulators.StatelessAccumulators import Negative
from PyFin.Math.Accumulators.StatelessAccumulators import XAverage
from PyFin.Math.Accumulators.StatelessAccumulators import StatelessSingleValueAccumulator
from PyFin.Math.Accumulators.IAccumulators import Pow
from PyFin.Utilities import pyFinAssert
from PyFin.Utilities import isClose
from PyFin.Math.Accumulators.impl import Deque


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
        self._deque = Deque(window)

    @property
    def size(self):
        return self._deque.size()

    @property
    def isFull(self):
        return self._deque.isFull()

    def _dumpOneValue(self, value):
        return self._deque.dump(value)


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
        self._popout = self._dumpOneValue(self._valueHolder.result())

    def result(self):
        try:
            return self._popout
        except AttributeError:
            return np.nan


class SingleValuedValueHolder(StatefulValueHolder):
    def __init__(self, window, dependency):
        super(SingleValuedValueHolder, self).__init__(window, dependency)
        _checkParameterList(dependency)

    def _push(self, data):
        if not self._isValueHolderContained:
            try:
                value = data[self._dependency]
            except KeyError:
                value = np.nan
        else:
            self._dependency.push(data)
            value = self._dependency.result()
        return value


class SortedValueHolder(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(SortedValueHolder, self).__init__(window, dependency)
        self._sortedArray = []

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        if self._deque.isFull():
            popout = self._dumpOneValue(value)
            delPos = bisect.bisect_left(self._sortedArray, popout)
            del self._sortedArray[delPos]
            bisect.insort_left(self._sortedArray, value)
        else:
            self._dumpOneValue(value)
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
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        popout = self._dumpOneValue(value)
        if not math.isnan(popout):
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
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        popout = self._dumpOneValue(value)
        if not math.isnan(popout):
            self._runningSum += value - popout
        else:
            self._runningSum += value

    def result(self):
        try:
            return self._runningSum / self.size
        except ZeroDivisionError:
            return np.nan


class MovingPositiveAverage(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingPositiveAverage, self).__init__(window, dependency)
        self._runningPositiveSum = 0.0
        self._runningPositiveCount = 0

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
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


class MovingPositiveDifferenceAverage(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingPositiveDifferenceAverage, self).__init__(window, dependency)
        runningPositive = Positive(Latest(dependency) - Shift(Latest(dependency), 1))
        self._runningAverage = MovingAverage(window, dependency=runningPositive)

    def push(self, data):
        self._runningAverage.push(data)
        if self._isFull == 0 and self._runningAverage.isFull == 1:
            self._isFull = 1

    def result(self):
        return self._runningAverage.result()


class MovingNegativeDifferenceAverage(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingNegativeDifferenceAverage, self).__init__(window, dependency)
        runningNegative = Negative(Latest(dependency) - Shift(Latest(dependency), 1))
        self._runningAverage = MovingAverage(window, dependency=runningNegative)

    def push(self, data):
        self._runningAverage.push(data)
        if self._isFull == 0 and self._runningAverage.isFull:
            self._isFull = 1

    def result(self):
        return self._runningAverage.result()


class MovingRSI(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingRSI, self).__init__(window, dependency)
        self._posDiffAvg = MovingPositiveDifferenceAverage(window, dependency)
        self._negDiffAvg = MovingNegativeDifferenceAverage(window, dependency)

    def push(self, data):
        self._posDiffAvg.push(data)
        self._negDiffAvg.push(data)

        if self._isFull == 0 and self._posDiffAvg.isFull and self._negDiffAvg.isFull:
            self._isFull = 1

    def result(self):
        nominator = self._posDiffAvg.result()
        denominator = nominator - self._negDiffAvg.result()
        if denominator != 0.:
            return 100. * nominator / denominator
        else:
            return 50.


class MovingNegativeAverage(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingNegativeAverage, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
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
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        popout = self._dumpOneValue(value)
        if not math.isnan(popout):
            self._runningSum += value - popout
            self._runningSumSquare += value * value - popout * popout
        else:
            self._runningSum += value
            self._runningSumSquare += value * value

    def result(self):
        length = self._deque.size()

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


class MovingNegativeVariance(SingleValuedValueHolder):
    def __init__(self, window, dependency='x', isPopulation=False):
        super(MovingNegativeVariance, self).__init__(window, dependency)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
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
                return np.nan
        else:
            if self._runningNegativeCount >= 2:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / (length - 1)
            else:
                return np.nan


class MovingCountedPositive(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingCountedPositive, self).__init__(window, dependency)
        self._counts = 0

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
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
        value = self._push(data)
        if math.isnan(value):
            return np.nan
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
        try:
            if math.isnan(value):
                return np.nan
        except TypeError:
            if not value:
                return np.nan
        _ = self._dumpOneValue(value)

    def __getitem__(self, item):
        length = self.size
        if item >= length:
            raise ValueError("index {0} is out of the bound of the historical current length {1}".format(item, length))

        return self._deque[length - 1 - item]

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
        if math.isnan(value[0]) or math.isnan(value[1]):
            return np.nan
        popout = self._dumpOneValue(value)
        if not math.isnan(popout[0]):
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
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            if not isClose(denominator, 0.):
                denominator = math.sqrt(denominator)
                return nominator / denominator
            else:
                return 0.0
        else:
            return np.nan


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
        if math.isnan(sum(values)):
            return np.nan
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
        n = self.size
        if n >= 2:
            nominator = n * self._runningSumCrossSquare - self._runningSum * self._runningSum.T
            denominator = n * np.diag(self._runningSumCrossSquare) - self._runningSum * self._runningSum
            denominator = np.sqrt(denominator * denominator.T)
            return nominator / denominator
        else:
            return np.ones(len(self._runningSum)) * np.nan


class MovingProduct(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingProduct, self).__init__(window, dependency)
        self._runningProduct = 1.0

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        popout = self._dumpOneValue(value)
        if not math.isnan(popout):
            self._runningProduct *= value / popout
        else:
            self._runningProduct *= value

    def result(self):
        return self._runningProduct


class MovingCenterMoment(SingleValuedValueHolder):
    def __init__(self, window, order, dependency='x'):
        super(MovingCenterMoment, self).__init__(window, dependency)
        self._order = order

    def push(self, data):
        value = self._push(data)
        self._dumpOneValue(value)
        if math.isnan(value):
            return np.nan
        else:
            self._runningMoment = np.mean(np.power(np.abs(self._deque.as_array() - np.mean(self._deque.as_array())), self._order))

    def result(self):
        return self._runningMoment


class MovingSkewness(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingSkewness, self).__init__(window, dependency)
        self._runningStd3 = Pow(MovingVariance(window, dependency, isPopulation=True), 1.5)
        self._runningMoment3 = MovingCenterMoment(window, 3, dependency)
        self._runningSkewness = self._runningMoment3 / self._runningStd3

    def push(self, data):
        self._runningSkewness.push(data)

    def result(self):
        return self._runningSkewness.result()


class MovingMaxPos(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMaxPos, self).__init__(window, dependency)
        self._runningTsMaxPos = np.nan

    def push(self, data):
        super(MovingMaxPos, self).push(data)
        self._max = self._sortedArray[-1]

    def result(self):
        tmpList = self._deque.as_list()
        self._runningTsMaxPos = tmpList.index(self._max)
        return self._runningTsMaxPos


class MovingMinPos(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingMinPos, self).__init__(window, dependency)
        self._runningTsMinPos = np.nan

    def push(self, data):
        super(MovingMinPos, self).push(data)
        self._min = self._sortedArray[0]

    def result(self):
        tmpList = self._deque.as_list()
        self._runningTsMinPos = tmpList.index(self._min)
        return self._runningTsMinPos


class MovingKurtosis(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingKurtosis, self).__init__(window, dependency)
        self._runningStd4 = Pow(MovingVariance(window, dependency, isPopulation=True), 2)
        self._runningMoment4 = MovingCenterMoment(window, 4, dependency)
        self._runningKurtosis = self._runningMoment4 / self._runningStd4

    def push(self, data):
        self._runningKurtosis.push(data)

    def result(self):
        return self._runningKurtosis.result()


class MovingRSV(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingRSV, self).__init__(window, dependency)
        self._cached_value = None

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        else:
            self._dumpOneValue(value)
            self._cached_value = value

    def result(self):
        con = self._deque.as_list()
        return (self._cached_value - min(con)) / (max(con) - min(con))


class MACD(StatelessSingleValueAccumulator):
    def __init__(self, short, long, dependency='x', method=XAverage):
        super(MACD, self).__init__(dependency)
        self._short_average = method(window=short, dependency=dependency)
        self._long_average = method(window=long, dependency=dependency)

    def push(self, data):
        self._short_average.push(data)
        self._long_average.push(data)
        if self._isFull == 0 and self._short_average.isFull and self._long_average.isFull:
            self._isFull = 1

    def result(self):
        return self._short_average.result() - self._long_average.result()


class MovingRank(SortedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingRank, self).__init__(window, dependency)
        self._runningRank = []

    def result(self):
        self._runningRank = [bisect.bisect_left(self._sortedArray, x) for x in self._deque.as_list()]
        return self._runningRank


# runningJ can be more than 1 or less than 0.
class MovingKDJ(SingleValuedValueHolder):
    def __init__(self, window, k=3, d=3, dependency='x'):
        super(MovingKDJ, self).__init__(window, dependency)
        self._runningRsv = MovingRSV(window, dependency)
        self._k = k
        self._d = d

    def push(self, data):
        value = self._runningRsv.push(data)
        rsv = self._runningRsv.value
        if self.size == 0:
            self._dumpOneValue(value)
            self._runningJ = np.nan
        else:
            if self.size == 1:
                self._dumpOneValue(value)
                self._runningK = (0.5 * (self._k - 1) + rsv) / self._k
                self._runningD = (0.5 * (self._d - 1) + self._runningK) / self._d
            else:
                self._runningK = (self._runningK * (self._k - 1) + rsv) / self._k
                self._runningD = (self._runningD * (self._d - 1) + self._runningK) / self._d
            self._runningJ = 3 * self._runningK - 2 * self._runningD

    def result(self):
        return self._runningJ


class MovingAroon(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingAroon, self).__init__(window, dependency)

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        else:
            self._dumpOneValue(value)

    def result(self):
        tmpList = self._deque.as_list()
        self._runningAroonOsc = (tmpList.index(np.max(tmpList)) - tmpList.index(np.min(tmpList))) / self.window
        return self._runningAroonOsc


class MovingBias(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingBias, self).__init__(window, dependency)
        self._runningMa = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        else:
            self._dumpOneValue(value)
            self._runningBias = value / np.mean(self._deque.as_array()) - 1

    def result(self):
        return self._runningBias


class MovingLevel(SingleValuedValueHolder):
    def __init__(self, window, dependency='x'):
        super(MovingLevel, self).__init__(window, dependency)
        self._runningLevel = 1

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        else:
            self._dumpOneValue(value)
            if self.size > 1:
                con = self._deque.as_list()
                self._runningLevel = con[-1] / con[0]

    def result(self):
        return self._runningLevel


class MovingAutoCorrelation(SingleValuedValueHolder):
    def __init__(self, window, lags, dependency='x'):
        super(MovingAutoCorrelation, self).__init__(window, dependency)
        self._lags = lags
        if window <= lags:
            raise ValueError("lags should be less than window however\n"
                             "window is: {0} while lags is: {1}".format(window, lags))

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        else:
            self._dumpOneValue(value)

    def result(self):
        tmp_list = self._deque.as_list()
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


if __name__ == '__main__':

    s = Shift(MovingAverage(2, 'x'), 1)
    s.push({'x': 2})
    s.push({'x': 3})
    print(s.result())