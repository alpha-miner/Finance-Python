# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

import copy
import numpy as np
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder
from PyFin.Analysis.SecurityValueHolders import SecuritiesValues
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMinimum
from PyFin.Math.Accumulators.StatefulAccumulators import MovingSum
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCountedPositive
from PyFin.Math.Accumulators.StatefulAccumulators import MovingPositiveAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingHistoricalWindow
from PyFin.Math.Accumulators.Performancers import MovingLogReturn


class SecuritySingleValueHolder(SecurityValueHolder):
    def __init__(self, window, HolderType, dependency='x', symbolList=None):
        super(SecuritySingleValueHolder, self).__init__(dependency, symbolList)
        self._window = window

        if isinstance(dependency, SecurityValueHolder):
            self._symbolList = dependency.symbolList
            self._window = window + dependency.window - 1
            self._dependency = dependency._dependency
            self._innerHolders = \
                {
                    name: HolderType(window, copy.deepcopy(dependency.holders[name])) for name in self._symbolList
                    }

        else:
            self._innerHolders = \
                {
                    name: HolderType(window, self._dependency) for name in self._symbolList
                    }


class SecurityMovingAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingAverage, self).__init__(window, MovingAverage, dependency, symbolList)


class SecurityMovingMax(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingMax, self).__init__(window, MovingMax, dependency, symbolList)


class SecurityMovingMinimum(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingMinimum, self).__init__(window, MovingMinimum, dependency, symbolList)


class SecurityMovingSum(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingSum, self).__init__(window, MovingSum, dependency, symbolList)


class SecurityMovingCountedPositive(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingCountedPositive, self).__init__(window, MovingCountedPositive, dependency, symbolList)


class SecurityMovingPositiveAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingPositiveAverage, self).__init__(window, MovingPositiveAverage, dependency, symbolList)


class SecurityMovingLogReturn(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingLogReturn, self).__init__(window, MovingLogReturn, dependency, symbolList)


class SecurityMovingHistoricalWindow(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityMovingHistoricalWindow, self).__init__(window, MovingHistoricalWindow, dependency, symbolList)

    def __getitem__(self, item):
        if isinstance(item, str):
            return super(SecurityMovingHistoricalWindow, self).__getitem__(item)
        elif isinstance(item, int):
            res = {}
            for name in self._innerHolders:
                try:
                    res[name] = self._innerHolders[name].value[item]
                except ArithmeticError:
                    res[name] = np.nan
            return SecuritiesValues(res)
        else:
            raise ValueError("{0} is not recognized as valid int or string".forma(item))
