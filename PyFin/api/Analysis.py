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
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingVariance
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRSI
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingHistoricalWindow
from PyFin.Analysis.TechnicalAnalysis import SecurityLatestValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityXAverageValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMACDValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecuritySqrtValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityDiffValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecuritySimpleReturnValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityLogReturnValueHolder


def EMA(window, dependency='x'):
    return SecurityXAverageValueHolder(window, dependency)


def MACD(short, long, dependency='x'):
    return SecurityMACDValueHolder(short, long, dependency)


def RSI(window, dependency='x'):
    return SecurityMovingRSI(window, dependency)


def MA(window, dependency='x'):
    return SecurityMovingAverage(window, dependency)


def MAX(window, dependency='x'):
    return SecurityMovingMax(window, dependency)


def MIN(window, dependency='x'):
    return SecurityMovingMinimum(window, dependency)


def SUM(window, dependency='x'):
    return SecurityMovingSum(window, dependency)


def VARIANCE(window, dependency='x'):
    return SecurityMovingVariance(window, dependency)


def NPOSITIVE(window, dependency='x'):
    return SecurityMovingCountedPositive(window, dependency)


def MAPOSITIVE(window, dependency='x'):
    return SecurityMovingPositiveAverage(window, dependency)


def HIST(window, dependency='x'):
    return SecurityMovingHistoricalWindow(window, dependency)


def LAST(dependency='x'):
    return SecurityLatestValueHolder(dependency)


def SQRT(dependency='x'):
    return SecuritySqrtValueHolder(dependency)


def DIFF(dependency='x'):
    return SecurityDiffValueHolder(dependency)


def RETURNSimple(dependency='x'):
    return SecuritySimpleReturnValueHolder(dependency)


def RETURNLog(dependency='x'):
    return SecurityLogReturnValueHolder(dependency)


HIGH = functools.partial(LAST, 'high')
LOW = functools.partial(LAST, 'low')
OPEN = functools.partial(LAST, 'open')
CLOSE = functools.partial(LAST, 'close')



