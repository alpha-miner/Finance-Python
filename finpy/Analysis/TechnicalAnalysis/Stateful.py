# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

import copy
import numpy as np
from finpy.Analysis.SecurityValueHolders import SecurityValueHolder
from finpy.Analysis.SecurityValueHolders import SecuritiesValues
from finpy.Math.Accumulators.StatefulAccumulators import MovingAverage
from finpy.Math.Accumulators.StatefulAccumulators import MovingMax
from finpy.Math.Accumulators.StatefulAccumulators import MovingMinimum
from finpy.Math.Accumulators.StatefulAccumulators import MovingSum
from finpy.Math.Accumulators.StatefulAccumulators import MovingCountedPositive
from finpy.Math.Accumulators.StatefulAccumulators import MovingPositiveAverage
from finpy.Math.Accumulators.StatefulAccumulators import MovingHistoricalWindow
from finpy.Math.Accumulators.Performancers import MovingLogReturn


class SecuritySingleValueHolder(SecurityValueHolder):

    def __init__(self, window, HolderType, pNames='x', symbolList=None):
        super(SecuritySingleValueHolder, self).__init__(pNames, symbolList)
        self._window = window

        if isinstance(pNames, SecurityValueHolder):
            self._symbolList = pNames.symbolList
            self._window = window + pNames.window - 1
            self._pNames = pNames._pNames
            self._innerHolders = \
                {
                    name: HolderType(window, copy.deepcopy(pNames._innerHolders[name])) for name in self._symbolList
                }

        else:
            self._innerHolders = \
                {
                    name: HolderType(window, self._pNames) for name in self._symbolList
                }


class SecurityMovingAverage(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingAverage, self).__init__(window, MovingAverage, pNames,  symbolList)


class SecurityMovingMax(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingMax, self).__init__(window, MovingMax, pNames,  symbolList)


class SecurityMovingMinimum(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingMinimum, self).__init__(window, MovingMinimum, pNames,  symbolList)


class SecurityMovingSum(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingSum, self).__init__(window, MovingSum, pNames,  symbolList)


class SecurityMovingCountedPositive(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingCountedPositive, self).__init__(window, MovingCountedPositive, pNames,  symbolList)


class SecurityMovingPositiveAverage(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingPositiveAverage, self).__init__(window, MovingPositiveAverage, pNames,  symbolList)


class SecurityMovingLogReturn(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingLogReturn, self).__init__(window, MovingLogReturn, pNames,  symbolList)


class SecurityMovingHistoricalWindow(SecuritySingleValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingHistoricalWindow, self).__init__(window, MovingHistoricalWindow, pNames,  symbolList)

    def __getitem__(self, item):
        if isinstance(item, str):
            return super(SecurityMovingHistoricalWindow, self).__getitem__(item)
        elif isinstance(item, int):
            res = {}
            for name in self._innerHolders:
                try:
                    res[name] = self._innerHolders[name].value[item]
                except:
                    res[name] = np.nan
            return SecuritiesValues(res)
        else:
            raise RuntimeError("{0} is not recognized as valid int or string".forma(item))



