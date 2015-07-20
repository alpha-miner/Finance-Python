# -*- coding: utf-8 -*-
u"""
Created on 2015-7-17

@author: cheng.li
"""

from finpy.Risk.Accumulators import MovingAverager
from finpy.Risk.Accumulators import MovingVariancer
from finpy.Risk.Accumulators import MovingCorrelation
import math


class MovingSharp(object):

    def __init__(self, window):
        self._mean = MovingAverager(window)
        self._var = MovingVariancer(window, False)
        self._window = window
        self._len = 0

    def push(self, value, benchmark=0.0):
        '''
        @value: annualized return value
        @benchmark: annualized benchmark treasury bond yield
        '''
        self._mean.push(value - benchmark)
        self._var.push(value)
        self._len += 1

    def result(self):
        if self._mean.isFull:
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
        if self._pReturnMean.isFull:
            corr = self._correlationHolder.result()
            pStd = math.sqrt(self._pReturnVar.result())
            mStd = math.sqrt(self._mReturnVar.result())
            beta = corr * pStd / mStd
            alpha = self._pReturnMean.result() - beta * self._mReturnMean.result()
            return alpha, beta


