# -*- coding: utf-8 -*-
u"""
Created on 2015-7-25

@author: cheng.li
"""

from finpy.Risk.IAccumulators import Accumulator

class StatelessAccumulator(Accumulator):

    def __init__(self, pNames='x'):
        super(StatelessAccumulator, self).__init__(pNames)
        self._currentMax = None
        self._returnSize = 1
        self._dependency = 0


class Max(StatelessAccumulator):
    def __init__(self, pNames='x'):
        super(Max, self).__init__(pNames)
        self._currentMax = None
        self._returnSize = 1

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        if self._currentMax is None:
            self._currentMax = value
        else:
            if self._currentMax < value:
                self._currentMax = value

    def result(self):
        return self._currentMax


class Minum(StatelessAccumulator):
    def __init__(self, pNames='x'):
        super(Minum, self).__init__(pNames)
        self._currentMin = None
        self._returnSize = 1

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        if self._currentMin is None:
            self._currentMin = value
        else:
            if self._currentMin > value:
                self._currentMin = value

    def result(self):
        return self._currentMin


class Sum(StatelessAccumulator):
    def __init__(self, pNames='x'):
        super(Sum, self).__init__(pNames)
        self._currentSum = 0.0
        self._returnSize = 1

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        self._currentSum += value

    def result(self):
        return self._currentSum


class Average(StatelessAccumulator):
    def __init__(self, pNames='x'):
        super(Average, self).__init__(pNames)
        self._currentSum = 0.0
        self._currentCount = 0
        self._returnSize = 1

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        self._currentSum += value
        self._currentCount += 1

    def result(self):
        return self._currentSum / self._currentCount

