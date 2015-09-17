# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMinimum
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingSum
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingCountedPositive
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingPositiveAverage
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingHistoricalWindow
from PyFin.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingLogReturn

__all__ = ['SecurityMovingAverage',
           'SecurityMovingMax',
           'SecurityMovingMinimum',
           'SecurityMovingSum',
           'SecurityMovingCountedPositive',
           'SecurityMovingPositiveAverage',
           'SecurityMovingHistoricalWindow',
           'SecurityMovingLogReturn']
