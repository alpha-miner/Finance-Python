# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

import copy
import numpy as np
cimport numpy as np
cimport cython
from PyFin.Math.Accumulators.IAccumulators cimport Accumulator
from PyFin.Analysis.SeriesValues cimport SeriesValues
from PyFin.Analysis.SecurityValueHolders cimport SecurityValueHolder
from PyFin.Analysis.SecurityValueHolders cimport build_holder
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingMin
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingRank
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingQuantile
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingAllTrue
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingAnyTrue
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingSum
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingStandardDeviation
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingCountedPositive
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingPositiveAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingCountedNegative
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingNegativeAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingPositiveDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingNegativeDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingRSI
from PyFin.Math.Accumulators.StatefulAccumulators cimport MovingLogReturn
from PyFin.Math.MathConstants cimport NAN


cdef class SecuritySingleValueHolder(SecurityValueHolder):
    def __init__(self, window, holderType, x):
        super(SecuritySingleValueHolder, self).__init__()
        self._compHolder = build_holder(x) if isinstance(x, SecurityValueHolder) else None
        if self._compHolder:
            self._dependency = self._compHolder.fields
            self._window = window + self._compHolder.window
            self._holderTemplate = holderType(window=window, x=str(self._compHolder))
            self._innerHolders = {
                name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
                }
        else:
            self._dependency = [x]
            self._window = window
            self._holderTemplate = holderType(window=window, x=self._dependency)


cdef class SecurityMovingAverage(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingAverage, self).__init__(window, MovingAverage, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MA}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingMax(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingMax, self).__init__(window, MovingMax, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MMax}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingMin(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingMin, self).__init__(window, MovingMin, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MMin}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingRank(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingRank, self).__init__(window, MovingRank, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MRank}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingQuantile(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingQuantile, self).__init__(window, MovingQuantile, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MQuantile}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingAllTrue(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingAllTrue, self).__init__(window, MovingAllTrue, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MAllTrue}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingAnyTrue(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingAnyTrue, self).__init__(window, MovingAnyTrue, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MAnyTrue}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingSum(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingSum, self).__init__(window, MovingSum, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MSum}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingVariance(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingVariance, self).__init__(window, MovingVariance, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MVariance}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingStandardDeviation(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingStandardDeviation, self).__init__(window, MovingStandardDeviation, x)

    def __str__(self):
        if self._compHolder:
            return "\\mathrm{{MStd}}({0}, {1})".format(self._window - self._compHolder.window, str(self._compHolder))
        else:
            return str(self._holderTemplate)


cdef class SecurityMovingCountedPositive(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingCountedPositive, self).__init__(window, MovingCountedPositive, x)


cdef class SecurityMovingPositiveAverage(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingPositiveAverage, self).__init__(window, MovingPositiveAverage, x)


cdef class SecurityMovingCountedNegative(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingCountedNegative, self).__init__(window, MovingCountedNegative, x)


cdef class SecurityMovingNegativeAverage(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingNegativeAverage, self).__init__(window, MovingNegativeAverage, x)


cdef class SecurityMovingPositiveDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingPositiveDifferenceAverage, self).__init__(window, MovingPositiveDifferenceAverage, x)


cdef class SecurityMovingNegativeDifferenceAverage(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingNegativeDifferenceAverage, self).__init__(window, MovingNegativeDifferenceAverage, x)


cdef class SecurityMovingRSI(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingRSI, self).__init__(window, MovingRSI, x)


cdef class SecurityMovingLogReturn(SecuritySingleValueHolder):
    def __init__(self, window, x):
        super(SecurityMovingLogReturn, self).__init__(window, MovingLogReturn, x)
