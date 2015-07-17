# -*- coding: utf-8 -*-
u"""
Created on 2015-7-17

@author: cheng.li
"""

from finpy.Risk.Accumulators import MovingAverager
from finpy.Risk.Accumulators import MovingVariancer
import math


class MovingSharp(object):

    def __init__(self, window, timeMul=252):
        self._mean = MovingAverager(window)
        self._var = MovingVariancer(window, False)
        self._window = window
        self._len = 0
        self._timeMul = timeMul

    def push(self, value, benchmark=0.0):
        self._mean.push(value - benchmark)
        self._var.push(value)
        self._len += 1

    def result(self):
        if self._mean.isFull:
            return self._mean.result() * self._timeMul / math.sqrt(self._var.result()*self._timeMul)