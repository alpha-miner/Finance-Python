# -*- coding: utf-8 -*-
u"""
Created on 2015-7-17

@author: cheng.li
"""

from finpy.Risk.Accumulators import ValueHolder
from finpy.Risk.Accumulators import MovingAverager
from finpy.Risk.Accumulators import MovingVariancer
from finpy.Risk.Accumulators import MovingCorrelation
import math


class MovingSharp(object):

    def __init__(self, window):
        self._mean = MovingAverager(window)
        self._var = MovingVariancer(window, False)
        self._window = window

    def push(self, value, benchmark=0.0):
        '''
        @value: annualized return value
        @benchmark: annualized benchmark treasury bond yield
        '''
        self._mean.push(value - benchmark)
        self._var.push(value)

    def result(self):
        if len(self._mean._con) >= 2:
            return self._mean.result() / math.sqrt(self._var.result())


class MovingAlphaBeta(object):

    def __init__(self, window):
        self._pReturnMean = MovingAverager(window)
        self._mReturnMean = MovingAverager(window)
        self._pReturnVar = MovingVariancer(window)
        self._mReturnVar = MovingVariancer(window)
        self._correlationHolder = MovingCorrelation(window)

    def push(self, pReturn, mReturn, rf=0.0):
        self._pReturnMean.push(pReturn - rf)
        self._mReturnMean.push(mReturn - rf)
        self._pReturnVar.push(pReturn - rf)
        self._mReturnVar.push(mReturn - rf)
        self._correlationHolder.push((pReturn - rf, mReturn - rf))

    def result(self):
        if len(self._pReturnMean._con) >= 2:
            corr = self._correlationHolder.result()
            pStd = math.sqrt(self._pReturnVar.result())
            mStd = math.sqrt(self._mReturnVar.result())
            beta = corr * pStd / mStd
            alpha = self._pReturnMean.result() - beta * self._mReturnMean.result()
            return alpha, beta


class MovingDrawDown(ValueHolder):

    def __init__(self, window):
        super(MovingDrawDown, self).__init__(window)
        self._highIndex = 0
        self._secondHighIndex = 0
        self._runningIndex = -1
        self._highCumReturn = 0.0
        self._secondHighCumReturn = 0.0
        self._runningCumReturn = 0.0
        self._rollDown = 0.0

    def push(self, value):
        '''
        :param value: expected to be exponential annualized return
        :return:
        '''
        popout = self._dumpOneValue(value)
        self._runningIndex += 1
        self._runningCumReturn += value

        # when high == second high == current
        if self._highIndex == self._secondHighIndex and self._secondHighIndex == self._runningIndex:
            if value >= 0.0:
                self._highIndex += 1
                self._highCumReturn += value
                self._secondHighIndex += 1
                self._secondHighCumReturn += value
        # when only second high == current
        elif self._secondHighIndex == (self._runningIndex - 1):
            if value > 0.0:
                self._secondHighIndex += 1
                self._secondHighCumReturn += value

        self._rollDown += popout

        # check should high or second high start to roll down
        if self._runningIndex >= ((0 if self._highIndex < 0 else self._highIndex) + self._window):
            self._highCumReturn = self._rollDown
            self._highIndex += 1
            if self._runningIndex >= ((0 if self._secondHighIndex < 0 else self._secondHighIndex) + self._window):
                self._secondHighCumReturn = self._rollDown
                self._secondHighIndex += 1

        # check whether running sum replace highs
        if self._runningCumReturn >= self._secondHighCumReturn:
            self._secondHighIndex = self._runningIndex
            self._secondHighCumReturn = self._runningCumReturn
            if self._runningCumReturn >= self._highCumReturn:
                self._highIndex = self._runningIndex
                self._highCumReturn = self._runningCumReturn

        # check whether highs changes
        if self._highCumReturn < self._secondHighCumReturn:
            self._highIndex = self._secondHighIndex
            self._highCumReturn = self._secondHighCumReturn

        # if high == second high != running
        # make second high == running
        if self._highIndex == self._secondHighIndex and self._highIndex != self._runningIndex:
            self._secondHighIndex = self._runningIndex
            self._secondHighCumReturn = self._runningCumReturn

    def result(self):
        return self._runningCumReturn - self._highCumReturn, self._runningIndex - self._highIndex, \
               self._highIndex, self._secondHighIndex, self._runningIndex


if __name__ == "__main__":
    mv = MovingDrawDown(5)

    value = [-0.01, -0.05, -0.02, 0.03, 0.04, 0.03, -0.01, 0.005, -0.02, -0.04, 0.2]

    for v in value:
        mv.push(v)
        print(mv.result())










