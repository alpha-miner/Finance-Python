# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""


import functools

from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMin
from PyFin.Analysis.TechnicalAnalysis import SecurityMaximumValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMinimumValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingQuantile
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAllTrue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAnyTrue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingSum
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingVariance
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingStandardDeviation
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRSI
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingHistoricalWindow
from PyFin.Analysis.TechnicalAnalysis import SecuritySignValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityXAverageValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMACDValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecuritySqrtValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityDiffValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecuritySimpleReturnValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityLogReturnValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityExpValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityLogValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityPowValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityAbsValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityAcosValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityAcoshValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityAsinValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityAsinhValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingResidue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCorrelation
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRank
from PyFin.Analysis.SecurityValueHolders import SecurityShiftedValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityIIFValueHolder


from PyFin.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSAverageAdjustedSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSQuantileSecurityValueHolder


def CSRank(dependency):
    return CSRankedSecurityValueHolder(dependency)


def CSMean(dependency):
    return CSAverageSecurityValueHolder(dependency)


def CSMeanAdjusted(dependency):
    return CSAverageAdjustedSecurityValueHolder(dependency)


def CSQuantile(dependency):
    return CSQuantileSecurityValueHolder(dependency)


def CSPercentile(percent, dependency):
    return CSPercentileSecurityValueHolder(percent, dependency)


def CSZScore(dependency):
    return CSZScoreSecurityValueHolder(dependency)


def SIGN(dependency='x'):
    return SecuritySignValueHolder(dependency)


def EMA(window, dependency='x'):
    return SecurityXAverageValueHolder(window, dependency)


def MACD(short, long, dependency='x'):
    return SecurityMACDValueHolder(short, long, dependency)


def RSI(window, dependency='x'):
    return SecurityMovingRSI(window, dependency)


def RES(window, dependency=('y', 'x')):
    return SecurityMovingResidue(window, dependency)


def CORR(window, dependency=('x', 'y')):
    return SecurityMovingCorrelation(window, dependency)


def RANK(window, dependency='x'):
    return SecurityMovingRank(window, dependency)


def MA(window, dependency='x'):
    return SecurityMovingAverage(window, dependency)


def MMAX(window, dependency='x'):
    return SecurityMovingMax(window, dependency)


def MMIN(window, dependency='x'):
    return SecurityMovingMin(window, dependency)


def MAXIMUM(dependency=('x', 'y')):
    return SecurityMaximumValueHolder(dependency)


def MINIMUM(dependency=('x', 'y')):
    return SecurityMinimumValueHolder(dependency)


def MQUANTILE(window, dependency='x'):
    return SecurityMovingQuantile(window, dependency)


def MALLTRUE(window, dependency='x'):
    return SecurityMovingAllTrue(window, dependency)


def MANYTRUE(window, dependency='x'):
    return SecurityMovingAnyTrue(window, dependency)


def MSUM(window, dependency='x'):
    return SecurityMovingSum(window, dependency)


def MVARIANCE(window, dependency='x'):
    return SecurityMovingVariance(window, dependency)


def MSTD(window, dependency='x'):
    return SecurityMovingStandardDeviation(window, dependency)


def MNPOSITIVE(window, dependency='x'):
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


def EXP(dependency):
    return SecurityExpValueHolder(dependency)


def LOG(dependency):
    return SecurityLogValueHolder(dependency)


def POW(dependency, n):
    return SecurityPowValueHolder(dependency, n)


def ABS(dependency):
    return SecurityAbsValueHolder(dependency)


def ACOS(dependency):
    return SecurityAcosValueHolder(dependency)


def ACOSH(dependency):
    return SecurityAcoshValueHolder(dependency)


def ASIN(dependency):
    return SecurityAsinValueHolder(dependency)


def ASINH(dependency):
    return SecurityAsinhValueHolder(dependency)


def SHIFT(dependency, n):
    return SecurityShiftedValueHolder(dependency, n)


def IIF(flag, left, right):
    return SecurityIIFValueHolder(flag, left, right)


HIGH = functools.partial(LAST, 'high')
LOW = functools.partial(LAST, 'low')
OPEN = functools.partial(LAST, 'open')
CLOSE = functools.partial(LAST, 'close')



