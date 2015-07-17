# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""


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

        popout = 0.0
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


class MovingVariancer(ValueHolder):

    def __init__(self, window, isPopulation = True):
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

