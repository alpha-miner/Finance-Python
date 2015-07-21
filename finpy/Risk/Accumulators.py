# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import math


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

