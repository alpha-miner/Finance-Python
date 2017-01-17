# -*- coding: utf-8 -*-
u"""
Created on 2015-7-25

@author: cheng.li
"""

import math
import numpy as np
from PyFin.Math.Accumulators.IAccumulators import Accumulator
from PyFin.Math.Accumulators.IAccumulators import Pow
from PyFin.Math.Accumulators.IAccumulators import StatelessSingleValueAccumulator
import bisect


def _checkParameterList(dependency):
    if not isinstance(dependency, Accumulator) and len(dependency) > 1 and not isinstance(dependency, str):
        raise ValueError("This value holder (e.g. Max or Minimum) can't hold more than 2 parameter names ({0})"
                         " provided".format(dependency))


class Sign(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Sign, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._sign = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        self._isFull = 1
        if value > 0.:
            self._sign = 1.
        elif value < 0.:
            self._sign = -1.
        else:
            self._sign = 0.

    def result(self):
        return self._sign


class Diff(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Diff, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = np.nan
        self._curr = np.nan
        self._previous = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return math.isnan
        self._isFull = 1
        self._previous = self._curr
        self._curr = value

    def result(self):
        return self._curr - self._previous


class SimpleReturn(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(SimpleReturn, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = np.nan
        self._curr = np.nan
        self._previous = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        self._isFull = 1
        self._previous = self._curr
        self._curr = value

    def result(self):
        try:
            return self._curr / self._previous - 1.
        except ValueError:
            return np.nan


class LogReturn(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(LogReturn, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._diff = np.nan
        self._curr = np.nan
        self._previous = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan
        self._isFull = 1
        self._previous = self._curr
        self._curr = value

    def result(self):
        try:
            return math.log(self._curr / self._previous)
        except ValueError:
            return np.nan


class Positive(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Positive, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._pos = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        if value > 0.:
            self._pos = value
        elif value <= 0.:
            self._pos = 0.
        else:
            self._pos = np.nan

    def result(self):
        return self._pos


class Negative(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Negative, self).__init__(dependency)
        _checkParameterList(dependency)
        self._returnSize = 1
        self._neg = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        if value < 0.:
            self._neg = value
        elif value >= 0.:
            self._neg = 0.
        else:
            self._neg = np.nan

    def result(self):
        return self._neg


class Max(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Max, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMax = np.nan
        self._returnSize = 1
        self._first = True

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        if self._first:
            self._currentMax = value
            self._first = False
        else:
            if self._currentMax < value:
                self._currentMax = value

    def result(self):
        return self._currentMax


class Minimum(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Minimum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentMin = np.nan
        self._returnSize = 1
        self._first = True

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        if self._first:
            self._currentMin = value
            self._first = False
        else:
            if self._currentMin > value:
                self._currentMin = value

    def result(self):
        return self._currentMin


class Sum(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Sum, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = np.nan
        self._returnSize = 1
        self._first = True

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        if self._first:
            self._currentSum = value
            self._first = False
        else:
            self._currentSum += value

    def result(self):
        return self._currentSum


class Average(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Average, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = np.nan
        self._currentCount = 0
        self._returnSize = 1

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

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


class XAverage(StatelessSingleValueAccumulator):
    def __init__(self, window, dependency='x'):
        super(XAverage, self).__init__(dependency)
        self._average = 0.0
        self._exp = 2.0 / (window + 1.)
        self._count = 0

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        if self._count == 0:
            self._average = value
        else:
            self._average += self._exp * (value - self._average)
        self._count += 1

    def result(self):
        return self._average


class Variance(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x', isPopulation=False):
        super(Variance, self).__init__(dependency)
        _checkParameterList(dependency)
        self._currentSum = 0.0
        self._currentSumSquare = 0.0
        self._currentCount = 0
        self._isPop = isPopulation
        self._returnSize = 1

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        self._currentSum += value
        self._currentSumSquare += value * value
        self._currentCount += 1

    def result(self):
        tmp = self._currentSumSquare - self._currentSum * self._currentSum / self._currentCount

        pop_num = self._currentCount if self._isPop else self._currentCount - 1

        if pop_num:
            return tmp / pop_num
        else:
            return np.nan


class Product(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Product,self).__init__(dependency)
        self._product = 1.0

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        self._product *= value

    def result(self):
        return self._product


class CenterMoment(StatelessSingleValueAccumulator):
    def __init__(self, order, dependency='x'):
        super(CenterMoment, self).__init__(dependency)
        self._this_list = []
        self._order = order
        self._moment = np.nan

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        self._this_list.append(value)
        self._moment = np.mean(np.power(np.abs(np.array(self._this_list) - np.mean(self._this_list)), self._order))

    def result(self):
        return self._moment


class Skewness(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Skewness, self).__init__(dependency)
        self._std3 = Pow(Variance(dependency, isPopulation=True), 1.5)
        self._moment3 = CenterMoment(3, dependency)
        self._skewness = self._moment3 / self._std3

    def push(self, data):
        self._skewness.push(data)

    def result(self):
        return self._skewness.result()


class Kurtosis(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Kurtosis, self).__init__(dependency)
        self._std4 = Pow(Variance(dependency, isPopulation=True), 2)
        self._moment4 = CenterMoment(4, dependency)
        self._kurtosis = self._moment4 / self._std4

    def push(self, data):
        self._kurtosis.push(data)

    def result(self):
        return self._kurtosis.result()


class Rank(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(Rank, self).__init__(dependency)
        self._thisList = []
        self._sortedList = []
        self._rank = []

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        self._thisList.append(value)
        self._sortedList = sorted(self._thisList)

    def result(self):
        self._rank = [bisect.bisect_left(self._sortedList, x) for x in self._thisList]
        return self._rank


class LevelList(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x', ):
        super(LevelList, self).__init__(dependency)
        self._levelList = []
        self._thisList = []

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        self._thisList.append(value)
        if len(self._thisList) == 1:
            self._levelList.append(1.0)
        else:
            self._levelList.append(self._thisList[-1] / self._thisList[0])

    def result(self):
        return self._levelList


class LevelValue(StatelessSingleValueAccumulator):
    def __init__(self, dependency='x'):
        super(LevelValue, self).__init__(dependency)
        self._thisList = []

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1

        self._thisList.append(value)
        if len(self._thisList) == 1:
            self._levelValue = 1.0
        else:
            self._levelValue = self._thisList[-1] / self._thisList[0]

    def result(self):
        return self._levelValue


class AutoCorrelation(StatelessSingleValueAccumulator):
    def __init__(self, lags, dependency='x'):
        super(AutoCorrelation, self).__init__(dependency)
        self._lags = lags
        self._thisList = []

    def push(self, data):
        value = self._push(data)
        if math.isnan(value):
            return np.nan

        self._isFull = 1
        self._thisList.append(value)

    def result(self):
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
                return np.nan
            return self._AutoCorrMatrix[0, 1]


class StatelessMultiValueAccumulator(Accumulator):
    def __init__(self, dependency):
        super(StatelessMultiValueAccumulator, self).__init__(dependency)
        self._returnSize = 1
        self._window = 1
        self._containerSize = 1

    def _push(self, data):
        if not self._isValueHolderContained:
            try:
                value = [data[name] for name in self._dependency]
            except KeyError:
                value = [np.nan] * len(self._dependency)
        else:
            self._dependency.push(data)
            value = self._dependency.result()
        return value


class Correlation(StatelessMultiValueAccumulator):
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
        value = self._push(data)
        if math.isnan(value[0]) or math.isnan(value[1]):
            return np.nan

        self._isFull = 1

        self._runningSumLeft = self._runningSumLeft + value[0]
        self._runningSumRight = self._runningSumRight + value[1]
        self._runningSumSquareLeft = self._runningSumSquareLeft + value[0] * value[0]
        self._runningSumSquareRight = self._runningSumSquareRight + value[1] * value[1]
        self._runningSumCrossSquare = self._runningSumCrossSquare + value[0] * value[1]
        self._currentCount += 1

    def result(self):
        n = self._currentCount
        nominator = n * self._runningSumCrossSquare - self._runningSumLeft * self._runningSumRight
        denominator = (n * self._runningSumSquareLeft - self._runningSumLeft * self._runningSumLeft) \
                      * (n * self._runningSumSquareRight - self._runningSumRight * self._runningSumRight)
        denominator = math.sqrt(denominator)
        if denominator != 0:
            return nominator / denominator
        else:
            return np.nan