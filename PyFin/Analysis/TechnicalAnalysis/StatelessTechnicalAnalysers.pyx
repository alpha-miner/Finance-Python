# -*- coding: utf-8 -*-
u"""
Created on 2015-2-12

@author: cheng.li
"""

import copy
from PyFin.Analysis.SecurityValueHolders cimport SecurityValueHolder
from PyFin.Math.Accumulators.IAccumulators cimport Sign
from PyFin.Math.Accumulators.StatelessAccumulators cimport XAverage
from PyFin.Math.Accumulators.StatefulAccumulators cimport MACD
from PyFin.Math.Accumulators.IAccumulators cimport Exp
from PyFin.Math.Accumulators.IAccumulators cimport Log
from PyFin.Math.Accumulators.IAccumulators cimport Pow
from PyFin.Math.Accumulators.IAccumulators cimport Sqrt
from PyFin.Math.Accumulators.IAccumulators cimport Abs
from PyFin.Math.Accumulators.IAccumulators cimport Acos
from PyFin.Math.Accumulators.IAccumulators cimport Acosh
from PyFin.Math.Accumulators.IAccumulators cimport Asin
from PyFin.Math.Accumulators.IAccumulators cimport Asinh
from PyFin.Math.Accumulators.StatelessAccumulators cimport Maximum
from PyFin.Math.Accumulators.StatelessAccumulators cimport Minimum
from PyFin.Math.Accumulators.StatelessAccumulators cimport Diff
from PyFin.Math.Accumulators.StatelessAccumulators cimport SimpleReturn
from PyFin.Math.Accumulators.StatelessAccumulators cimport LogReturn


cdef class SecurityStatelessSingleValueHolder(SecurityValueHolder):
    def __init__(self, holderType, dependency='x', **kwargs):
        super(SecurityStatelessSingleValueHolder, self).__init__(dependency)
        if self._compHolder:
            self._holderTemplate = holderType(dependency='x', **kwargs)
            self._innerHolders = {
                name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
                }
        else:
            self._holderTemplate = holderType(dependency=self._dependency, **kwargs)


cdef class SecurityXAverageValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityXAverageValueHolder, self).__init__(holderType=XAverage,
                                                          dependency=dependency,
                                                          window=window)


cdef class SecurityMACDValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, short_win, long_win, dependency='x'):
        super(SecurityMACDValueHolder, self).__init__(holderType=MACD,
                                                      dependency=dependency,
                                                      short_win=short_win,
                                                      long_win=long_win)


cdef class SecuritySignValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySignValueHolder, self).__init__(holderType=Sign,
                                                      dependency=dependency)


cdef class SecurityExpValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityExpValueHolder, self).__init__(holderType=Exp,
                                                     dependency=dependency)


cdef class SecurityLogValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogValueHolder, self).__init__(holderType=Log,
                                                     dependency=dependency)


cdef class SecurityPowValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', n=1):
        super(SecurityPowValueHolder, self).__init__(holderType=Pow,
                                                     dependency=dependency,
                                                     n=n)


cdef class SecuritySqrtValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySqrtValueHolder, self).__init__(holderType=Sqrt,
                                                      dependency=dependency)


cdef class SecurityAbsValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAbsValueHolder, self).__init__(holderType=Abs,
                                                     dependency=dependency)


cdef class SecurityAcosValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcosValueHolder, self).__init__(holderType=Acos,
                                                      dependency=dependency)


cdef class SecurityAcoshValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcoshValueHolder, self).__init__(holderType=Acosh,
                                                       dependency=dependency)


cdef class SecurityAsinValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinValueHolder, self).__init__(holderType=Asin,
                                                      dependency=dependency)

cdef class SecurityAsinhValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinhValueHolder, self).__init__(holderType=Asinh,
                                                       dependency=dependency)


cdef class SecurityDiffValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityDiffValueHolder, self).__init__(holderType=Diff,
                                                      dependency=dependency)


cdef class SecuritySimpleReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySimpleReturnValueHolder, self).__init__(holderType=SimpleReturn,
                                                              dependency=dependency)


cdef class SecurityLogReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogReturnValueHolder, self).__init__(holderType=LogReturn,
                                                           dependency=dependency)


cdef class SecurityMaximumValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency=('x', 'y')):
        super(SecurityMaximumValueHolder, self).__init__(holderType=Maximum,
                                                         dependency=dependency)


cdef class SecurityMinimumValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency=('x', 'y')):
        super(SecurityMinimumValueHolder, self).__init__(holderType=Minimum,
                                                         dependency=dependency)
