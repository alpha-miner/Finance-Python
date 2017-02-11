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

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityXAverageValueHolder(2.0 / self._holderTemplate._exp - 1,
                                               self._compHolder)
        else:
            return SecurityXAverageValueHolder(2.0 / self._holderTemplate._exp - 1,
                                               self._dependency)


class SecurityMACDValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, short, long, dependency='x'):
        super(SecurityMACDValueHolder, self).__init__(holderType=MACD,
                                                      dependency=dependency,
                                                      short_win=short,
                                                      long_win=long)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMACDValueHolder(2. / self._holderTemplate._short_average._exp - 1.,
                                           2. / self._holderTemplate._long_average._exp - 1.,
                                           self._compHolder)
        else:
            return SecurityMACDValueHolder(2. / self._holderTemplate._short_average._exp - 1.,
                                           2. / self._holderTemplate._long_average._exp - 1.,
                                           self._dependency)


class SecuritySignValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySignValueHolder, self).__init__(holderType=Sign,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecuritySignValueHolder(self._compHolder)
        else:
            return SecuritySignValueHolder(self._dependency)


class SecurityExpValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityExpValueHolder, self).__init__(holderType=Exp,
                                                     dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityExpValueHolder(self._compHolder)
        else:
            return SecurityExpValueHolder(self._dependency)


class SecurityLogValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogValueHolder, self).__init__(holderType=Log,
                                                     dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityLogValueHolder(self._compHolder)
        else:
            return SecurityLogValueHolder(self._dependency)


class SecurityPowValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', n=1):
        super(SecurityPowValueHolder, self).__init__(holderType=Pow,
                                                     dependency=dependency,
                                                     n=n)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityPowValueHolder(self._compHolder, self._holderTemplate._n)
        else:
            return SecurityPowValueHolder(self._dependency, self._holderTemplate._n)


class SecuritySqrtValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySqrtValueHolder, self).__init__(holderType=Sqrt,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecuritySqrtValueHolder(self._compHolder)
        else:
            return SecuritySqrtValueHolder(self._dependency)


class SecurityAbsValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAbsValueHolder, self).__init__(holderType=Abs,
                                                     dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAbsValueHolder(self._compHolder)
        else:
            return SecurityAbsValueHolder(self._dependency)


class SecurityAcosValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcosValueHolder, self).__init__(holderType=Acos,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAcosValueHolder(self._compHolder)
        else:
            return SecurityAcosValueHolder(self._dependency)


class SecurityAcoshValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcoshValueHolder, self).__init__(holderType=Acosh,
                                                       dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAcoshValueHolder(self._compHolder)
        else:
            return SecurityAcoshValueHolder(self._dependency)


class SecurityAsinValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinValueHolder, self).__init__(holderType=Asin,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAsinValueHolder(self._compHolder)
        else:
            return SecurityAsinValueHolder(self._dependency)


class SecurityAsinhValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinhValueHolder, self).__init__(holderType=Asinh,
                                                       dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAsinhValueHolder(self._compHolder)
        else:
            return SecurityAsinhValueHolder(self._dependency)


class SecurityDiffValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityDiffValueHolder, self).__init__(holderType=Diff,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityDiffValueHolder(self._compHolder)
        else:
            return SecurityDiffValueHolder(self._dependency)


class SecuritySimpleReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySimpleReturnValueHolder, self).__init__(holderType=SimpleReturn,
                                                              dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecuritySimpleReturnValueHolder(self._compHolder)
        else:
            return SecuritySimpleReturnValueHolder(self._dependency)


class SecurityLogReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogReturnValueHolder, self).__init__(holderType=LogReturn,
                                                           dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityLogReturnValueHolder(self._compHolder)
        else:
            return SecurityLogReturnValueHolder(self._dependency)
