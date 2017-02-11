# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

import copy
import numpy as np
from PyFin.Analysis.SecurityValues import SecurityValues
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMinimum
from PyFin.Math.Accumulators.StatefulAccumulators import MovingQuantile
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAllTrue
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAnyTrue
from PyFin.Math.Accumulators.StatefulAccumulators import MovingSum
from PyFin.Math.Accumulators.StatefulAccumulators import MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCountedPositive
from PyFin.Math.Accumulators.StatefulAccumulators import MovingPositiveAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCountedNegative
from PyFin.Math.Accumulators.StatefulAccumulators import MovingNegativeAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingPositiveDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingNegativeDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingRSI
from PyFin.Math.Accumulators.StatefulAccumulators import MovingHistoricalWindow
from PyFin.Math.Accumulators.StatefulAccumulators import MovingLogReturn


class SecuritySingleValueHolder(SecurityValueHolder):
    def __init__(self, window, HolderType, dependency='x'):
        super(SecuritySingleValueHolder, self).__init__(dependency)
        self._window += window
        if self._compHolder:
            self._holderTemplate = HolderType(window=window, dependency='x')
            self._innerHolders = {
                name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
                }
        else:
            self._holderTemplate = HolderType(window=window, dependency=self._dependency)


class SecurityMovingAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAverage, self).__init__(window, MovingAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingAverage(self._window, self._dependency)


class SecurityMovingMax(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingMax, self).__init__(window, MovingMax, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingMax(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingMax(self._window, self._dependency)


class SecurityMovingMinimum(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingMinimum, self).__init__(window, MovingMinimum, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingMinimum(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingMinimum(self._window, self._dependency)


class SecurityMovingQuantile(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingQuantile, self).__init__(window, MovingQuantile, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingQuantile(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingQuantile(self._window, self._dependency)


class SecurityMovingAllTrue(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAllTrue, self).__init__(window, MovingAllTrue, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingAllTrue(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingAllTrue(self._window, self._dependency)


class SecurityMovingAnyTrue(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingAnyTrue, self).__init__(window, MovingAnyTrue, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingAnyTrue(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingAnyTrue(self._window, self._dependency)


class SecurityMovingSum(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingSum, self).__init__(window, MovingSum, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingSum(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingSum(self._window, self._dependency)


class SecurityMovingVariance(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingVariance, self).__init__(window, MovingVariance, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingVariance(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingVariance(self._window, self._dependency)


class SecurityMovingCountedPositive(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingCountedPositive, self).__init__(window, MovingCountedPositive, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingCountedPositive(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingCountedPositive(self._window, self._dependency)


class SecurityMovingPositiveAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingPositiveAverage, self).__init__(window, MovingPositiveAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingPositiveAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingPositiveAverage(self._window, self._dependency)


class SecurityMovingCountedNegative(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingCountedNegative, self).__init__(window, MovingCountedNegative, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingCountedNegative(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingCountedNegative(self._window, self._dependency)


class SecurityMovingNegativeAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingNegativeAverage, self).__init__(window, MovingNegativeAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingNegativeAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingNegativeAverage(self._window, self._dependency)


class SecurityMovingPositiveDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingPositiveDifferenceAverage, self).__init__(window, MovingPositiveDifferenceAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingPositiveDifferenceAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingPositiveDifferenceAverage(self._window, self._dependency)


class SecurityMovingNegativeDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingNegativeDifferenceAverage, self).__init__(window, MovingNegativeDifferenceAverage, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingNegativeDifferenceAverage(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingNegativeDifferenceAverage(self._window, self._dependency)


class SecurityMovingRSI(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingRSI, self).__init__(window, MovingRSI, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingRSI(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingRSI(self._window, self._dependency)


class SecurityMovingLogReturn(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingLogReturn, self).__init__(window, MovingLogReturn, dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingLogReturn(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingLogReturn(self._window, self._dependency)


class SecurityMovingHistoricalWindow(SecuritySingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityMovingHistoricalWindow, self).__init__(window, MovingHistoricalWindow, dependency)

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
            return SecurityValues(res)
        else:
            raise ValueError("{0} is not recognized as valid int or string".format(item))

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMovingHistoricalWindow(self._window - self._compHolder._window, self._compHolder)
        else:
            return SecurityMovingHistoricalWindow(self._window, self._dependency)


if __name__ == '__main__':

    from PyFin.api import MA

    t = MA(1, 'x') < MA(1, 'y')

    data = {'aapl': {'x': 4, 'y': 3},
            'goog': {'x': 1, 'y': 4}
            }

    t.push(data)

    print(t.value)
    print(t._dependency)

    for k, v in t.value.iteritems():
        print(k, v)