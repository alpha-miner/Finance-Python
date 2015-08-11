# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

from finpy.Analysis.SecurityValueHolders import SecurityValueHolder
from finpy.Math.Accumulators.StatefulAccumulators import MovingAverage
from finpy.Math.Accumulators.StatefulAccumulators import MovingMax
from finpy.Math.Accumulators.StatefulAccumulators import MovingMinimum
from finpy.Math.Accumulators.StatefulAccumulators import MovingSum
from finpy.Math.Accumulators.StatefulAccumulators import MovingCountedPositive
from finpy.Math.Accumulators.StatefulAccumulators import MovingPositiveAverage
from finpy.Math.Accumulators.Performancers import MovingLogReturn


class SecuritySingleValueHolder(SecurityValueHolder):

    def __init__(self, window, HolderType, pNames='x', symbolList=None):
        super(SecuritySingleValueHolder, self).__init__(pNames, symbolList)
        self._window = window

        if isinstance(pNames, SecurityValueHolder):
            self._symbolList = pNames.symbolList
            self._innerHolders = \
                {
                    name: HolderType(self._window, pNames._innerHolders[name]) for name in self._symbolList
                }

        else:
            self._innerHolders = \
                {
                    name: HolderType(self._window, self._pNames) for name in self._symbolList
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


if __name__ == "__main__":
    s1 = SecurityMovingMax(10, 'close', ['AAPL', 'IBM'])
    s2 = SecurityMovingMinimum(20, 'open', ['IBM', 'AAPL'])
    s3 = SecurityMovingMinimum(20, 'PE', ['IBM', 'AAPL'])
    s3 = 3 + s1['AAPL'] * s3['AAPL'] + 4
    print(s3.dependency)
