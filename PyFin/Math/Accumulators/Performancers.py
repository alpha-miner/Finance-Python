# -*- coding: utf-8 -*-
u"""
Created on 2015-7-17

@author: cheng.li
"""

import math
import numpy as np
from PyFin.Math.Accumulators.StatefulAccumulators import StatefulValueHolder
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingNegativeVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCorrelation
from PyFin.Math.Accumulators.StatefulAccumulators import SingleValuedValueHolder


class MovingLogReturn(SingleValuedValueHolder):
    def __init__(self, window=1, dependency='price'):
        super(MovingLogReturn, self).__init__(window, dependency)
        self._runningReturn = np.nan

    def push(self, data):
        value = super(MovingLogReturn, self).push(data)
        if value is None:
            return
        popout = self._dumpOneValue(value)
        if popout is not np.nan and popout != 0.0:
            self._runningReturn = math.log(value / popout)

    def result(self):
        if self.size >= self.window:
            return self._runningReturn
        else:
            raise ArithmeticError("Container has less than 2 samples")


class MovingSharp(StatefulValueHolder):
    def __init__(self, window, dependency=('ret', 'riskFree')):
        super(MovingSharp, self).__init__(window, dependency)
        self._mean = MovingAverage(window, dependency='x')
        self._var = MovingVariance(window, dependency='x', isPopulation=False)

    def push(self, data):
        value = super(MovingSharp, self).push(data)
        ret = value[0]
        benchmark = value[1]
        data = {'x': ret - benchmark}
        self._mean.push(data)
        self._var.push(data)

    def result(self):
        return self._mean.result() / math.sqrt(self._var.result())


class MovingSortino(StatefulValueHolder):
    def __init__(self, window, dependency=('ret', 'riskFree')):
        super(MovingSortino, self).__init__(window, dependency)
        self._mean = MovingAverage(window, dependency='x')
        self._negativeVar = MovingNegativeVariance(window, dependency='x')

    def push(self, data):
        value = super(MovingSortino, self).push(data)
        if value is None:
            return
        ret = value[0]
        benchmark = value[1]
        data = {'x': ret - benchmark}
        self._mean.push(data)
        self._negativeVar.push(data)

    def result(self):
        return self._mean.result() / math.sqrt(self._negativeVar.result())


class MovingAlphaBeta(StatefulValueHolder):
    def __init__(self, window, dependency=('pRet', 'mRet', 'riskFree')):
        self._returnSize = 2
        super(MovingAlphaBeta, self).__init__(window, dependency)
        self._pReturnMean = MovingAverage(window, dependency='x')
        self._mReturnMean = MovingAverage(window, dependency='y')
        self._pReturnVar = MovingVariance(window, dependency='x')
        self._mReturnVar = MovingVariance(window, dependency='y')
        self._correlationHolder = MovingCorrelation(window, dependency=['x', 'y'])

    def push(self, data):
        value = super(MovingAlphaBeta, self).push(data)
        if value is None:
            return
        pReturn = value[0]
        mReturn = value[1]
        rf = value[2]
        data = {'x': pReturn - rf, 'y': mReturn - rf}
        self._pReturnMean.push(data)
        self._mReturnMean.push(data)
        self._pReturnVar.push(data)
        self._mReturnVar.push(data)
        self._correlationHolder.push(data)

    def result(self):
        corr = self._correlationHolder.result()
        pStd = math.sqrt(self._pReturnVar.result())
        mStd = math.sqrt(self._mReturnVar.result())
        beta = corr * pStd / mStd
        alpha = self._pReturnMean.result() - beta * self._mReturnMean.result()
        return alpha, beta


class MovingDrawDown(StatefulValueHolder):
    def __init__(self, window, dependency='ret'):
        super(MovingDrawDown, self).__init__(window, dependency)
        self._returnSize = 3
        self._maxer = MovingMax(window + 1, dependency='x')
        self._maxer.push(dict(x=0.0))
        self._runningCum = 0.0
        self._highIndex = 0
        self._runningIndex = 0

    def push(self, data):
        value = super(MovingDrawDown, self).push(data)
        if value is None:
            return
        self._runningIndex += 1
        self._runningCum += value
        self._maxer.push(dict(x=self._runningCum))
        self._currentMax = self._maxer.result()
        if self._runningCum >= self._currentMax:
            self._highIndex = self._runningIndex

    def result(self):
        return self._runningCum - self._currentMax, self._runningIndex - self._highIndex, self._highIndex


class MovingAverageDrawdown(StatefulValueHolder):
    def __init__(self, window, dependency='ret'):
        super(MovingAverageDrawdown, self).__init__(window, dependency)
        self._returnSize = 2
        self._drawdownCalculator = MovingDrawDown(window, dependency='ret')
        self._drawdownMean = MovingAverage(window, dependency='drawdown')
        self._durationMean = MovingAverage(window, dependency='duration')

    def push(self, data):
        value = super(MovingAverageDrawdown, self).push(data)
        if value is None:
            return
        self._drawdownCalculator.push(dict(ret=value))
        drawdown, duration, _ = self._drawdownCalculator.result()
        self._drawdownMean.push(dict(drawdown=drawdown))
        self._durationMean.push(dict(duration=duration))

    def result(self):
        return self._drawdownMean.result(), self._durationMean.result()


class MovingMaxDrawdown(StatefulValueHolder):
    def __init__(self, window, dependency='ret'):
        super(MovingMaxDrawdown, self).__init__(window, dependency)
        self._returnSize = 2
        self._drawdownCalculator = MovingDrawDown(window, 'x')

    def push(self, data):
        value = super(MovingMaxDrawdown, self).push(data)
        if value is None:
            return
        self._drawdownCalculator.push(dict(x=value))
        drawdown, duration, _ = self._drawdownCalculator.result()
        self._dumpOneValue((drawdown, duration))

    def result(self):
        sortedValue = sorted(range(self.size), key=lambda x: self._con[x][0])
        return self._con[sortedValue[0]]
