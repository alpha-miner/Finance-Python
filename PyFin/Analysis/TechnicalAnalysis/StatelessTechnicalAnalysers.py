# -*- coding: utf-8 -*-
u"""
Created on 2015-10-22

@author: cheng.li
"""

import copy
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder
from PyFin.Math.Accumulators import Sign
from PyFin.Math.Accumulators import XAverage
from PyFin.Math.Accumulators import MACD
from PyFin.Math.Accumulators import Exp
from PyFin.Math.Accumulators import Log
from PyFin.Math.Accumulators import Pow
from PyFin.Math.Accumulators import Sqrt
from PyFin.Math.Accumulators import Abs
from PyFin.Math.Accumulators import Acos
from PyFin.Math.Accumulators import Acosh
from PyFin.Math.Accumulators import Asin
from PyFin.Math.Accumulators import Asinh
from PyFin.Math.Accumulators import Diff
from PyFin.Math.Accumulators import SimpleReturn
from PyFin.Math.Accumulators import LogReturn


class SecurityStatelessSingleValueHolder(SecurityValueHolder):
    def __init__(self, holderType, dependency='x', **kwargs):
        super(SecurityStatelessSingleValueHolder, self).__init__(dependency)
        if self._compHolder:
            self._holderTemplate = holderType(dependency='x', **kwargs)
            self._innerHolders = {
                name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
                }
        else:
            self._holderTemplate = holderType(dependency=self._dependency, **kwargs)


class SecurityXAverageValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, window, dependency='x'):
        super(SecurityXAverageValueHolder, self).__init__(holderType=XAverage,
                                                          dependency=dependency,
                                                          window=window)


class SecurityMACDValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, short, long, dependency='x'):
        super(SecurityMACDValueHolder, self).__init__(holderType=MACD,
                                                      dependency=dependency,
                                                      short=short,
                                                      long=long)


class SecuritySignValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySignValueHolder, self).__init__(holderType=Sign,
                                                      dependency=dependency)


class SecurityExpValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityExpValueHolder, self).__init__(holderType=Exp,
                                                     dependency=dependency)


class SecurityLogValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogValueHolder, self).__init__(holderType=Log,
                                                     dependency=dependency)


class SecurityPowValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityPowValueHolder, self).__init__(holderType=Pow,
                                                     dependency=dependency)


class SecuritySqrtValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySqrtValueHolder, self).__init__(holderType=Sqrt,
                                                      dependency=dependency)


class SecurityAbsValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAbsValueHolder, self).__init__(holderType=Abs,
                                                     dependency=dependency)


class SecurityAcosValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcosValueHolder, self).__init__(holderType=Acos,
                                                      dependency=dependency)


class SecurityAcoshValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcoshValueHolder, self).__init__(holderType=Acosh,
                                                       dependency=dependency)


class SecurityAsinValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinValueHolder, self).__init__(holderType=Asin,
                                                      dependency=dependency)


class SecurityAsinhValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinhValueHolder, self).__init__(holderType=Asinh,
                                                       dependency=dependency)


class SecurityDiffValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityDiffValueHolder, self).__init__(holderType=Diff,
                                                      dependency=dependency)


class SecuritySimpleReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySimpleReturnValueHolder, self).__init__(holderType=SimpleReturn,
                                                              dependency=dependency)


class SecurityLogReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogReturnValueHolder, self).__init__(holderType=LogReturn,
                                                           dependency=dependency)
