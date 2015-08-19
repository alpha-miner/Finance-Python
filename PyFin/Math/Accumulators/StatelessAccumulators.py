# -*- coding: utf-8 -*-
u"""
Created on 2015-7-25

@author: cheng.li
"""

import math
from PyFin.Math.Accumulators.IAccumulators import Accumulator
from PyFin.Math.Accumulators.StatefulAccumulators import _checkParameterList


class StatelessAccumulator(Accumulator):
    def __init__(self, dependency='x'):
        super(StatelessAccumulator, self).__init__(dependency)
        self._currentMax = None
        self._returnSize = 1
        self._window = 1
        self._containerSize = 1


class Max(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Max, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMax = None
        self._returnSize = 1

    def push(self, data):
        value = super(Max, self).push(data)
        if value is None:
            return
        if self._currentMax is None:
            self._currentMax = value
        else:
            if self._currentMax < value:
                self._currentMax = value

    def result(self):
        return self._currentMax


class Minimum(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Minimum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMin = None
        self._returnSize = 1

    def push(self, data):
        value = super(Minimum, self).push(data)
        if value is None:
            return
        if self._currentMin is None:
            self._currentMin = value
        else:
            if self._currentMin > value:
                self._currentMin = value

    def result(self):
        return self._currentMin


class Sum(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Sum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = 0.0
        self._returnSize = 1

    def push(self, data):
        value = super(Sum, self).push(data)
        if value is None:
            return
        self._currentSum += value

    def result(self):
        return self._currentSum


class Average(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Average, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = 0.0
        self._currentCount = 0
        self._returnSize = 1

    def push(self, data):
        value = super(Average, self).push(data)
        self._currentSum += value
        self._currentCount += 1

    def result(self):
        return self._currentSum / self._currentCount


class Variance(StatelessAccumulator):
    def __init__(self, dependency='x', isPopulation=False):
        super(Variance, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = 0.0
        self._currentSumSquare = 0.0
        self._currentCount = 0
        self._isPop = isPopulation
        self._returnSize = 1

    def push(self, data):
        value = super(Variance, self).push(data)
        if value is None:
            return
        self._currentSum += value
        self._currentSumSquare += value * value
        self._currentCount += 1

    def result(self):
        tmp = self._currentSumSquare - self._currentSum * self._currentSum / self._currentCount

        if self._isPop:
            return tmp / self._currentCount
        else:
            if self._currentCount >= 2:
                return tmp / (self._currentCount - 1)
            else:
                raise ZeroDivisionError("Container has too few samples: {0:d}".format(self._currentCount))


class Correlation(StatelessAccumulator):
    def __init__(self, dependency=('x', 'y')):
        super(Correlation, self).__init__(dependency)
        self._runningSumLeft = 0.0
        self._runningSumRight = 0.0
        self._runningSumSquareLeft = 0.0
        self._runningSumSquareRight = 0.0
        self._runningSumCrossSquare = 0.0
        self._currentCount = 0
        self._returnSize = 1

    def push(self, data):
        value = super(Correlation, self).push(data)
        if value is None:
            return
        self._runningSumLeft = self._runningSumLeft + value[0]
        self._runningSumRight = self._runningSumRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare + value[0] * value[1]
        self._currentCount += 1

    def result(self):
        if self._currentCount >= 2:
            n = self._currentCount
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        else:
            raise ZeroDivisionError("Container has less than 2 samples")
