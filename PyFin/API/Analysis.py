# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""


import functools
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMinimum
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingSum
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingHistoricalWindow
from PyFin.Analysis.TechnicalAnalysis import SecurityLatestValueHolder


def MA(window, dependency='x', symbolList=None):
    return SecurityMovingAverage(window, dependency, symbolList)


def MAX(window, dependency='x', symbolList=None):
    return SecurityMovingMax(window, dependency, symbolList)


def MIN(window, dependency='x', symbolList=None):
    return SecurityMovingMinimum(window, dependency, symbolList)


def SUM(window, dependency='x', symbolList=None):
    return SecurityMovingSum(window, dependency, symbolList)


def NPOSITIVE(window, dependency='x', symbolList=None):
    return SecurityMovingCountedPositive(window, dependency, symbolList)


def MAPOSITIVE(window, dependency='x', symbolList=None):
    return SecurityMovingPositiveAverage(window, dependency, symbolList)


def HIST(window, dependency='x', symbolList=None):
    return SecurityMovingHistoricalWindow(window, dependency, symbolList)


def LAST(dependency='x', symbolList=None):
    return SecurityLatestValueHolder(dependency, symbolList)

HIGH = functools.partial(LAST, 'high')
LOW = functools.partial(LAST, 'low')
OPEN = functools.partial(LAST, 'open')
CLOSE = functools.partial(LAST, 'close')



