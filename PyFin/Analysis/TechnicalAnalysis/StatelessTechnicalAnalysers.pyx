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

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityXAverageValueHolder(2.0 / self._holderTemplate._exp - 1,
                                               self._compHolder)
        else:
            return SecurityXAverageValueHolder(2.0 / self._holderTemplate._exp - 1,
                                               self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityXAverageValueHolder, (2.0 / self._holderTemplate._exp - 1, self._compHolder), d
        else:
            return SecurityXAverageValueHolder, (2.0 / self._holderTemplate._exp - 1, self._dependency), d

    def __setstate__(self, state):
        pass



cdef class SecurityMACDValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, short_win, long_win, dependency='x'):
        super(SecurityMACDValueHolder, self).__init__(holderType=MACD,
                                                      dependency=dependency,
                                                      short_win=short_win,
                                                      long_win=long_win)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMACDValueHolder(2. / self._holderTemplate._short_average._exp - 1.,
                                           2. / self._holderTemplate._long_average._exp - 1.,
                                           self._compHolder)
        else:
            return SecurityMACDValueHolder(2. / self._holderTemplate._short_average._exp - 1.,
                                           2. / self._holderTemplate._long_average._exp - 1.,
                                           self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityMACDValueHolder, (2. / self._holderTemplate._short_average._exp - 1.,
                                             2. / self._holderTemplate._long_average._exp - 1.,
                                             self._compHolder), d
        else:
            return SecurityMACDValueHolder, (2. / self._holderTemplate._short_average._exp - 1.,
                                             2. / self._holderTemplate._long_average._exp - 1.,
                                             self._dependency), d

    def __setstate__(self, state):
        pass


cdef class SecuritySignValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySignValueHolder, self).__init__(holderType=Sign,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecuritySignValueHolder(self._compHolder)
        else:
            return SecuritySignValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecuritySignValueHolder, (self._compHolder,), d
        else:
            return SecuritySignValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityExpValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityExpValueHolder, self).__init__(holderType=Exp,
                                                     dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityExpValueHolder(self._compHolder)
        else:
            return SecurityExpValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityExpValueHolder, (self._compHolder,), d
        else:
            return SecurityExpValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityLogValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogValueHolder, self).__init__(holderType=Log,
                                                     dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityLogValueHolder(self._compHolder)
        else:
            return SecurityLogValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityLogValueHolder, (self._compHolder,), d
        else:
            return SecurityLogValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityPowValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', n=1):
        super(SecurityPowValueHolder, self).__init__(holderType=Pow,
                                                     dependency=dependency,
                                                     n=n)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityPowValueHolder(self._compHolder, self._holderTemplate._n)
        else:
            return SecurityPowValueHolder(self._dependency, self._holderTemplate._n)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityPowValueHolder, (self._compHolder, self._holderTemplate._n), d
        else:
            return SecurityPowValueHolder, (self._dependency, self._holderTemplate._n), d

    def __setstate__(self, state):
        pass


cdef class SecuritySqrtValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySqrtValueHolder, self).__init__(holderType=Sqrt,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecuritySqrtValueHolder(self._compHolder)
        else:
            return SecuritySqrtValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecuritySqrtValueHolder, (self._compHolder,), d
        else:
            return SecuritySqrtValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityAbsValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAbsValueHolder, self).__init__(holderType=Abs,
                                                     dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAbsValueHolder(self._compHolder)
        else:
            return SecurityAbsValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityAbsValueHolder, (self._compHolder,), d
        else:
            return SecurityAbsValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityAcosValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcosValueHolder, self).__init__(holderType=Acos,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAcosValueHolder(self._compHolder)
        else:
            return SecurityAcosValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityAcosValueHolder, (self._compHolder,), d
        else:
            return SecurityAcosValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityAcoshValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAcoshValueHolder, self).__init__(holderType=Acosh,
                                                       dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAcoshValueHolder(self._compHolder)
        else:
            return SecurityAcoshValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityAcoshValueHolder, (self._compHolder,), d
        else:
            return SecurityAcoshValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityAsinValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinValueHolder, self).__init__(holderType=Asin,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAsinValueHolder(self._compHolder)
        else:
            return SecurityAsinValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityAsinValueHolder, (self._compHolder,), d
        else:
            return SecurityAsinValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityAsinhValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityAsinhValueHolder, self).__init__(holderType=Asinh,
                                                       dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityAsinhValueHolder(self._compHolder)
        else:
            return SecurityAsinhValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityAsinhValueHolder, (self._compHolder,), d
        else:
            return SecurityAsinhValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityDiffValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityDiffValueHolder, self).__init__(holderType=Diff,
                                                      dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityDiffValueHolder(self._compHolder)
        else:
            copied = SecurityDiffValueHolder(self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityDiffValueHolder, (self._compHolder,), d
        else:
            return SecurityDiffValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        self.copy_attributes(state, is_deep=False)


cdef class SecuritySimpleReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecuritySimpleReturnValueHolder, self).__init__(holderType=SimpleReturn,
                                                              dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecuritySimpleReturnValueHolder(self._compHolder)
        else:
            return SecuritySimpleReturnValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecuritySimpleReturnValueHolder, (self._compHolder,), d
        else:
            return SecuritySimpleReturnValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityLogReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLogReturnValueHolder, self).__init__(holderType=LogReturn,
                                                           dependency=dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityLogReturnValueHolder(self._compHolder)
        else:
            return SecurityLogReturnValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityLogReturnValueHolder, (self._compHolder,), d
        else:
            return SecurityLogReturnValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityMaximumValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency=('x', 'y')):
        super(SecurityMaximumValueHolder, self).__init__(holderType=Maximum,
                                                         dependency=dependency)
    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMaximumValueHolder(self._compHolder)
        else:
            return SecurityMaximumValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityMaximumValueHolder, (self._compHolder,), d
        else:
            return SecurityMaximumValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class SecurityMinimumValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency=('x', 'y')):
        super(SecurityMinimumValueHolder, self).__init__(holderType=Minimum,
                                                         dependency=dependency)
    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityMinimumValueHolder(self._compHolder)
        else:
            return SecurityMinimumValueHolder(self._dependency)

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityMinimumValueHolder, (self._compHolder,), d
        else:
            return SecurityMinimumValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        pass
