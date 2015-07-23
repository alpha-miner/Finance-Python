# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import math
import numpy as np


class ValueHolder(object):

    def __init__(self, window):
        assert window > 0, "window length should be greater than 0"
        self._window = window
        self._con = []
        self._isFull = 0
        self._start = 0

    @property
    def isFull(self):
        return self._isFull

    @property
    def size(self):
        return len(self._con)

    def _dumpOneValue(self, value):

        if not hasattr(value, '__iter__'):
            popout = 0.0
        else:
            popout = [0.0] * len(value)

        if self._isFull == 1:
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


class MovingMaxer(ValueHolder):

    def __init__(self, window):
        super(MovingMaxer, self).__init__(window)

    def push(self, value):
        _ = self._dumpOneValue(value)

    def result(self):
        return max(self._con)


class MovingMinumer(ValueHolder):

    def __init__(self, window):
        super(MovingMinumer, self).__init__(window)

    def push(self, value):
        _ = self._dumpOneValue(value)

    def result(self):
        return min(self._con)


class MovingSum(ValueHolder):

    def __init__(self, window):
        super(MovingSum, self).__init__(window)
        self._runningSum = 0.0

    def push(self, value):
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value

    def result(self):
        return self._runningSum


class MovingAverager(ValueHolder):

    def __init__(self, window):
        super(MovingAverager, self).__init__(window)
        self._runningSum = 0.0

    def push(self, value):
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value

    def result(self):
        if self._isFull:
            return self._runningSum / self._window
        else:
            return self._runningSum / len(self._con)

class MovingPositiveAverager(ValueHolder):

    def __init__(self, window):
        super(MovingPositiveAverager, self).__init__(window)
        self._runningPositiveSum = 0.0
        self._runningPositiveCount = 0

    def push(self, value):
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

class MovingNegativeAverager(ValueHolder):

    def __init__(self, window):
        super(MovingNegativeAverager, self).__init__(window)
        self._runningNegativeSum = 0.0
        self._runningNegativeCount = 0

    def push(self, value):
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


class MovingVariancer(ValueHolder):

    def __init__(self, window, isPopulation=False):
        super(MovingVariancer, self).__init__(window)
        self._runningSum = 0.0
        self._runningSumSquare = 0.0
        self._isPop = isPopulation

    def push(self, value):
        popout = self._dumpOneValue(value)
        self._runningSum = self._runningSum - popout + value
        self._runningSumSquare = self._runningSumSquare - popout * popout + value * value

    def result(self):
        if self._isFull:
            tmp = self._runningSumSquare - self._runningSum * self._runningSum / self._window
            if self._isPop:
                return tmp / self._window
            else:
                return tmp / (self._window - 1)
        elif len(self._con) >= 2:
            tmp = self._runningSumSquare - self._runningSum * self._runningSum / len(self._con)
            if self._isPop:
                return tmp / len(self._con)
            else:
                return tmp / (len(self._con) - 1)


class MovingNegativeVariancer(ValueHolder):

    def __init__(self, window, isPopulation=False):
        super(MovingNegativeVariancer, self).__init__(window)
        self._runningNegativeSum = 0.0
        self._runningNegativeSumSquare = 0.0
        self._runningNegativeCount = 0
        self._isPop = isPopulation

    def push(self, value):
        popout = self._dumpOneValue(value)
        if value < 0:
            self._runningNegativeSum = self._runningNegativeSum + value
            self._runningNegativeSumSquare = self._runningNegativeSumSquare + value * value
            self._runningNegativeCount += 1
        if popout < 0:
            self._runningNegativeSum = self._runningNegativeSum - popout
            self._runningNegativeSumSquare = self._runningNegativeSumSquare - popout * popout
            self._runningNegativeCount -= 1

    def result(self):
        if self._isPop:
            if self._runningNegativeCount >= 1:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / length
        else:
            if self._runningNegativeCount >= 2:
                length = self._runningNegativeCount
                tmp = self._runningNegativeSumSquare - self._runningNegativeSum * self._runningNegativeSum / length
                return tmp / (length - 1)


class MovingCountedPositive(ValueHolder):

    def __init__(self, window):
        super(MovingCountedPositive, self).__init__(window)
        self._counts = 0

    def push(self, value):
        popout = self._dumpOneValue(value)

        if value > 0:
            self._counts += 1
        if popout > 0:
            self._counts -= 1

    def result(self):
        return self._counts


class MovingCountedNegative(ValueHolder):

    def __init__(self, window):
        super(MovingCountedNegative, self).__init__(window)
        self._counts = 0

    def push(self, value):
        popout = self._dumpOneValue(value)

        if value < 0:
            self._counts += 1
        if popout < 0:
            self._counts -= 1

    def result(self):
        return self._counts


# Calculator for one pair of series
class MovingCorrelation(ValueHolder):

    def __init__(self, window):
        super(MovingCorrelation, self).__init__(window)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0

    def push(self, value):
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

        if self._isFull:
            n = self._window
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          *(n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        elif len(self._con) >= 2:
            n = len(self._con)
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          *(n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator


class MovingCorrelationMatrix(ValueHolder):

    def __init__(self, window):
        super(MovingCorrelationMatrix, self).__init__(window)

    def push(self, values):
        _ = self._dumpOneValue(values)

    def result(self):
        if len(self._con) >= 2:
            return np.corrcoef(np.matrix(self._con).T)





