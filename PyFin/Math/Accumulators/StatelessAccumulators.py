# -*- coding: utf-8 -*-
u"""
Created on 2015-7-25

@author: cheng.li
"""

import math
import numpy as np
from PyFin.Math.Accumulators.IAccumulators import Accumulator


def _checkParameterList(dependency):
    if not isinstance(dependency, Accumulator) and len(dependency) > 1 and not isinstance(dependency, str):
        raise ValueError("This value holder (e.g. Max or Minimum) can't hold more than 2 parameter names ({0})"
                         " provided".format(dependency))


class StatelessAccumulator(Accumulator):
    def __init__(self, dependency='x'):
        super(StatelessAccumulator, self).__init__(dependency)
        self._returnSize = 1
        self._window = 1
        self._containerSize = 1

    def push(self, data):
        value = super(StatelessAccumulator, self).push(data)

        try:
            bool_flag = np.all(np.isnan(value))
            if bool_flag:
                return np.nan
        except TypeError:
            pass

        self._isFull = 1
        return value


class Latest(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Latest, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._latest = np.nan

    def push(self, data):
        value = super(Latest, self).push(data)
        if np.isnan(value):
            return np.nan
        self._latest = value

    def result(self):
        return self._latest


class Positive(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Positive, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._pos = np.nan

    def push(self, data):
        value = super(Positive, self).push(data)
        if np.isnan(value):
            return np.nan

        if value > 0.:
            self._pos = value
        elif value <= 0.:
            self._pos = 0.
        else:
            self._pos = np.nan

    def result(self):
        return self._pos


class Negative(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Negative, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._neg = np.nan

    def push(self, data):
        value = super(Negative, self).push(data)
        if np.isnan(value):
            return np.nan

        if value < 0.:
            self._neg = value
        elif value >= 0.:
            self._neg = 0.
        else:
            self._neg = np.nan

    def result(self):
        return self._neg


class Max(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Max, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMax = np.nan
        self._returnSize = 1
        self._first = True

    def push(self, data):
        value = super(Max, self).push(data)
        if np.isnan(value):
            return np.nan
        if self._first:
            self._currentMax = value
            self._first = False
        else:
            if self._currentMax < value:
                self._currentMax = value

    def result(self):
        return self._currentMax


class Minimum(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Minimum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMin = np.nan
        self._returnSize = 1
        self._first = True

    def push(self, data):
        value = super(Minimum, self).push(data)
        if np.isnan(value):
            return np.nan
        if self._first:
            self._currentMin = value
            self._first = False
        else:
            if self._currentMin > value:
                self._currentMin = value

    def result(self):
        return self._currentMin


class Sum(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Sum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = np.nan
        self._returnSize = 1
        self._first = True

    def push(self, data):
        value = super(Sum, self).push(data)
        if np.isnan(value):
            return np.nan
        if self._first:
            self._currentSum = value
            self._first = False
        else:
            self._currentSum += value

    def result(self):
        return self._currentSum


class Average(StatelessAccumulator):
    def __init__(self, dependency='x'):
        super(Average, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = np.nan
        self._currentCount = 0
        self._returnSize = 1

    def push(self, data):
        value = super(Average, self).push(data)
        if np.isnan(value):
            return np.nan
        if self._currentCount == 0:
            self._currentSum = value
        else:
            self._currentSum += value
        self._currentCount += 1

    def result(self):
        try:
            return self._currentSum / self._currentCount
        except ZeroDivisionError:
            return np.nan


class XAverage(StatelessAccumulator):
    def __init__(self, window, dependency='x'):
        super(XAverage, self).__init__(dependency)
        self._average = 0.0
        self._exp = 2.0 / (window + 1.)
        self._count = 0

    def push(self, data):
        value = super(XAverage, self).push(data)
        if np.isnan(value):
            return np.nan
        if self._count == 0:
            self._average = value
        else:
            self._average += self._exp * (value - self._average)
        self._count += 1

    def result(self):
        return self._average


class MACD(StatelessAccumulator):
    def __init__(self, short, long, dependency='x'):
        super(MACD, self).__init__(dependency)
        self._short_average = XAverage(window=short, dependency=dependency)
        self._long_average = XAverage(window=long, dependency=dependency)

    def push(self, data):
        self._short_average.push(data)
        self._long_average.push(data)
        if self._isFull == 0 and self._short_average.isFull and self._long_average.isFull:
            self._isFull = 1

    def result(self):
        return self._short_average.result() - self._long_average.result()


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
        if np.isnan(value):
            return np.nan
        self._currentSum += value
        self._currentSumSquare += value * value
        self._currentCount += 1

    def result(self):
        tmp = self._currentSumSquare - self._currentSum * self._currentSum / self._currentCount

        pop_num = self._currentCount if self._isPop else self._currentCount - 1

        try:
            return tmp / pop_num
        except ZeroDivisionError:
            return np.nan


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
        if np.any(np.isnan(value)):
            return np.nan
        self._runningSumLeft = self._runningSumLeft + value[0]
        self._runningSumRight = self._runningSumRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare + value[0] * value[1]
        self._currentCount += 1

    def result(self):
        try:
            n = self._currentCount
            nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
            denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                          * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
            denominator = math.sqrt(denominator)
            return nominator / denominator
        except ZeroDivisionError:
                return np.nan
