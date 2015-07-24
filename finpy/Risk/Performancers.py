# -*- coding: utf-8 -*-
u"""
Created on 2015-7-17

@author: cheng.li
"""

from finpy.Risk.Accumulators import StatefulValueHolder
from finpy.Risk.Accumulators import MovingMaxer
from finpy.Risk.Accumulators import MovingAverager
from finpy.Risk.Accumulators import MovingVariancer
from finpy.Risk.Accumulators import MovingNegativeVariancer
from finpy.Risk.Accumulators import MovingCorrelation
import math


class MovingSharp(StatefulValueHolder):

    def __init__(self, window, pNames=['ret', 'riskFree']):
        super(MovingSharp, self).__init__(window, pNames)
        self._mean = MovingAverager(window, pNames='x')
        self._var = MovingVariancer(window, pNames='x', isPopulation=False)

    def push(self, **kwargs):
        '''
        @value: annualized return value
        @benchmark: annualized benchmark treasury bond yield
        '''
        value = kwargs[self._pNames[0]]
        benchmark = kwargs[self._pNames[1]]
        self._mean.push(x=value - benchmark)
        self._var.push(x=value - benchmark)

    def result(self):
        if self._var.size >= 2:
            return self._mean.result() / math.sqrt(self._var.result())
        else:
            raise RuntimeError("Container has less than 2 samples")


class MovingSortino(StatefulValueHolder):

    def __init__(self, window, pNames=['ret', 'riskFree']):
        super(MovingSortino, self).__init__(window, pNames)
        self._mean = MovingAverager(window, pNames='x')
        self._negativeVar = MovingNegativeVariancer(window, pNames='x')

    def push(self, **kwargs):
        value = kwargs[self._pNames[0]]
        benchmark = kwargs[self._pNames[1]]
        self._mean.push(x=value - benchmark)
        self._negativeVar.push(x=value - benchmark)

    def result(self):
        if self._mean.size >= 2:
            return self._mean.result() / math.sqrt(self._negativeVar.result())
        else:
            raise RuntimeError("Container has less than 2 samples")


class MovingAlphaBeta(StatefulValueHolder):

    def __init__(self, window, pNames=['pRet', 'mRet', 'riskFree']):
        super(MovingAlphaBeta, self).__init__(window, pNames)
        self._pReturnMean = MovingAverager(window, pNames='x')
        self._mReturnMean = MovingAverager(window, pNames='y')
        self._pReturnVar = MovingVariancer(window, pNames='x')
        self._mReturnVar = MovingVariancer(window, pNames='y')
        self._correlationHolder = MovingCorrelation(window, pNames=['x', 'y'])

    def push(self, **kwargs):
        pReturn = kwargs[self._pNames[0]]
        mReturn = kwargs[self._pNames[1]]
        rf = kwargs[self._pNames[2]]
        self._pReturnMean.push(x=pReturn - rf)
        self._mReturnMean.push(y=mReturn - rf)
        self._pReturnVar.push(x=pReturn - rf)
        self._mReturnVar.push(y=mReturn - rf)
        self._correlationHolder.push(x=pReturn - rf, y=mReturn - rf)

    def result(self):
        if self._pReturnMean.size >= 2:
            corr = self._correlationHolder.result()
            pStd = math.sqrt(self._pReturnVar.result())
            mStd = math.sqrt(self._mReturnVar.result())
            beta = corr * pStd / mStd
            alpha = self._pReturnMean.result() - beta * self._mReturnMean.result()
            return alpha, beta
        else:
            raise RuntimeError("Container has less than 2 samples")


class MovingDrawDown(StatefulValueHolder):

    def __init__(self, window, pNames='ret'):
        super(MovingDrawDown, self).__init__(window, pNames)
        self._maxer = MovingMaxer(window+1, pNames='x')
        self._maxer.push(x=0.0)
        self._runningCum = 0.0
        self._highIndex = 0
        self._runningIndex = 0

    def push(self, **kwargs):
        '''
        :param value: expected to be exponential annualized return
        :return:
        '''
        value = kwargs[self._pNames]
        self._runningIndex += 1
        self._runningCum += value
        self._maxer.push(x=self._runningCum)
        self._currentMax = self._maxer.result()
        if self._runningCum >= self._currentMax:
            self._highIndex = self._runningIndex

    def result(self):
        '''
        :return: (draw down, duration, high index)
        '''
        return self._runningCum - self._currentMax, self._runningIndex - self._highIndex, self._highIndex


class MovingAverageDrawdown(StatefulValueHolder):

    def __init__(self, window, pNames='ret'):
        super(MovingAverageDrawdown, self).__init__(window, pNames)
        self._drawdownCalculator = MovingDrawDown(window, pNames='x')
        self._drawdownMean = MovingAverager(window, pNames='x')
        self._durationMean = MovingAverager(window, pNames='x')

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        self._drawdownCalculator.push(x=value)
        drawdown, duration, _ = self._drawdownCalculator.result()
        self._drawdownMean.push(x=drawdown)
        self._durationMean.push(x=duration)

    def result(self):
        return self._drawdownMean.result(), self._durationMean.result()


class MovingMaxDrawdown(StatefulValueHolder):

    def __init__(self, window, pNames=['ret']):
        super(MovingMaxDrawdown, self).__init__(window, pNames)
        self._drawdownCalculator = MovingDrawDown(window, 'x')

    def push(self, **kwargs):
        value = kwargs[self._pNames]
        self._drawdownCalculator.push(x=value)
        drawdown, duration, _ = self._drawdownCalculator.result()
        self._dumpOneValue((drawdown, duration))

    def result(self):
        sortedValue = sorted(range(self.size), key=lambda x: self._con[x][0])
        return self._con[sortedValue[0]]












