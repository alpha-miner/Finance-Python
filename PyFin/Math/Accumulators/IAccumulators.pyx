# -*- coding: utf-8 -*-
#cython: embedsignature=True
u"""
Created on 2017-2-8

@author: cheng.li
"""

from copy import deepcopy
from libc.math cimport sqrt
from libc.math cimport fabs
from libc.math cimport log
from libc.math cimport exp
from libc.math cimport acos
from libc.math cimport acosh
from libc.math cimport asin
from libc.math cimport asinh
cimport cython
from libc.math cimport isnan
import numpy as np
cimport numpy as np
import pandas as pd
from PyFin.Utilities.Asserts cimport pyFinAssert


cdef class IAccumulator(object):

    def __add__(self, right):
        return AddedValueHolder(self, right)

    def __sub__(self, right):
        return MinusedValueHolder(self, right)

    def __mul__(self, right):
        return MultipliedValueHolder(self, right)

    def __div__(self, right):
        return DividedValueHolder(self, right)

    # only work for python 3
    def __truediv__(self, right):
        return DividedValueHolder(self, right)

    def __richcmp__(self, right, int op):
        if op == 0:
            return LtOperatorValueHolder(self, right)
        elif op == 1:
            return LeOperatorValueHolder(self, right)
        elif op == 4:
            return GtOperatorValueHolder(self, right)
        elif op == 5:
            return GeOperatorValueHolder(self, right)

    def __xor__(self, right):
        return ListedValueHolder(self, right)

    def __rshift__(self, right):
        if isinstance(right, IAccumulator):
            return CompoundedValueHolder(self, right)

        try:
            return right(self)
        except TypeError:
            raise ValueError('{0} is not recognized as a valid operator'.format(right))

    def __neg__(self):
        return Negative(self)

    def __getitem__(self, item):
        return TruncatedValueHolder(self, item)


cdef class Accumulator(IAccumulator):

    def __init__(self, dependency):
        self._isFull = 0
        self._window = 0
        self._returnSize = 1

        if isinstance(dependency, Accumulator):
            self._isValueHolderContained = 1
        else:
            self._isValueHolderContained = 0
        if hasattr(dependency, '__iter__') and len(dependency) >= 2:
            for name in dependency:
                pyFinAssert(isinstance(name, str), ValueError, '{0} in pNames should be a plain string. But it is {1}'
                         .format(name,type(name)))
            self._dependency = dependency
        elif hasattr(dependency, '__iter__') and len(dependency) == 1:
            for name in dependency:
                pyFinAssert(isinstance(name, str), ValueError, '{0} in pNames should be a plain string. But it is {1}'
                         .format(name,type(name)))
            self._dependency = dependency[0]
        elif hasattr(dependency, '__iter__'):
            raise ValueError("parameters' name list should not be empty")
        else:
            pyFinAssert(isinstance(dependency, str) or isinstance(dependency, Accumulator), ValueError,
                        '{0} in pNames should be a plain string or an value holder. But it is {1}'
                        .format(dependency, type(dependency)))
            self._dependency = deepcopy(dependency)

    cdef extract(self, dict data):
        cdef str p

        if not self._isValueHolderContained:
            try:
                return data[self._dependency]
            except (TypeError, KeyError) as _:
                try:
                    return tuple(data[p] for p in self._dependency)
                except KeyError:
                    return np.nan
        else:
            self._dependency.push(data)
            return self._dependency.result()

    cpdef push(self, dict data):
        pass

    cpdef object result(self):
        pass

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def transform(self, data, str name=None, to_sort=False):

        cdef int i
        cdef int k
        cdef np.ndarray[double, ndim=2] matrix_values
        cdef long n = len(data)
        cdef np.ndarray[double, ndim=1] output_values = np.zeros(n)
        cdef list columns
        cdef int column_length
        cdef dict data_dict

        if to_sort:
            data.sort_index(inplace=True)

        if not name:
            name = 'transformed'

        matrix_values = data.as_matrix()
        columns = data.columns.tolist()
        column_length = len(columns)

        data_dict = {columns[k]: 0 for k in range(column_length)}

        for i in range(n):
            for k in range(column_length):
                data_dict[columns[k]] = matrix_values[i, k]
            self.push(data_dict)
            output_values[i] = self.result()

        return pd.Series(output_values, index=data.index, name=name)

    @property
    def value(self):
        return self.result()

    cpdef int isFull(self):
        return self._isFull == 1

    @property
    def window(self):
        return self._window

    @property
    def valueSize(self):
        return self._returnSize

    @property
    def dependency(self):
        if isinstance(self._dependency, str) or hasattr(self._dependency, '__iter__'):
            return self._dependency
        else:
            return self._dependency.dependency

    def __deepcopy__(self, memo):
        return Accumulator(self._dependency)

    def __reduce__(self):
        d = {}

        return Accumulator, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Negative(Accumulator):

    def __init__(self, valueHolder):
        self._valueHolder = build_holder(valueHolder)
        self._returnSize = valueHolder.valueSize
        self._window = valueHolder.window
        self._dependency = deepcopy(valueHolder.dependency)
        self._isFull = 0

    cpdef push(self, dict data):
        self._valueHolder.push(data)
        if self._valueHolder.isFull():
            self._isFull = 1

    cpdef object result(self):
        res = self._valueHolder.result()
        try:
            return -res
        except TypeError:
            return [-r for r in res]

    def __deepcopy__(self, memo):
        return Negative(self._valueHolder)

    def __reduce__(self):
        d = {}

        return Negative, (self._valueHolder, ), d

    def __setstate__(self, state):
        pass


cdef class ListedValueHolder(Accumulator):

    def __init__(self, left, right):
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._left.valueSize + self._right.valueSize
        self._dependency = list(set(self._left.dependency).union(set(self._right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._isFull = 0

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._left.isFull() and self._right.isFull():
            self._isFull = 1

    cpdef object result(self):
        resLeft = self._left.result()
        resRight = self._right.result()

        if not hasattr(resLeft, '__iter__'):
            resLeft = np.array([resLeft])
        if not hasattr(resRight, '__iter__'):
            resRight = np.array([resRight])
        return np.concatenate([resLeft, resRight])

    def __deepcopy__(self, memo):
        return ListedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return ListedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class TruncatedValueHolder(Accumulator):

    def __init__(self, valueHolder, item):
        if valueHolder.valueSize == 1:
            raise TypeError("scalar valued holder ({0}) can't be sliced".format(valueHolder))
        if isinstance(item, slice):
            self._start = item.start
            self._stop = item.stop
            length = item.stop - item.start
            if length < 0:
                length += valueHolder.valueSize
            if length < 0:
                raise ValueError('start {0:d} and end {0:d} are not compatible'.format(item.start, item.stop))
            self._returnSize = length
        else:
            self._start = item
            self._stop = -1
            self._returnSize = 1

        self._valueHolder = build_holder(valueHolder)
        self._dependency = self._valueHolder.dependency
        self._window = valueHolder.window
        self._isFull = 0

    cpdef push(self, dict data):
        self._valueHolder.push(data)
        if self._valueHolder.isFull():
            self._isFull = 1

    cpdef object result(self):
        if self._stop == -1:
            return self._valueHolder.result()[self._start]
        return self._valueHolder.result()[self._start:self._stop]

    def __deepcopy__(self, memo):
        if self._stop == -1:
            item = self._start
        else:
            item = slice(self._start, self._stop)
        return TruncatedValueHolder(self._valueHolder, item)

    def __reduce__(self):
        d = {}

        if self._stop == -1:
            item = self._start
        else:
            item = slice(self._start, self._stop)

        return TruncatedValueHolder, (self._valueHolder, item), d

    def __setstate__(self, state):
        pass


cdef class CombinedValueHolder(Accumulator):

    def __init__(self, left, right):
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._left.valueSize
        self._dependency = list(set(self._left.dependency).union(set(self._right.dependency)))
        self._window = max(self._left.window, self._right.window)
        self._isFull = 0

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._left.isFull() and self._right.isFull():
            self._isFull = 1

    cpdef int isFull(self):
        if self._left.isFull() and self._right.isFull():
            return True
        else:
            return False

    def __deepcopy__(self, memo):
        return CombinedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return CombinedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class AddedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 + res2

    def __deepcopy__(self, memo):
        return AddedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return AddedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class MinusedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 - res2

    def __deepcopy__(self, memo):
        return MinusedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return MinusedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class MultipliedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 * res2

    def __deepcopy__(self, memo):
        return MultipliedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return MultipliedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class DividedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right)

    @cython.cdivision(True)
    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 / res2

    def __deepcopy__(self, memo):
        return DividedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return DividedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class LtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LtOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 < res2

    def __deepcopy__(self, memo):
        return LtOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return LtOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class LeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 <= res2

    def __deepcopy__(self, memo):
        return LeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return LeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class GtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GtOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 > res2

    def __deepcopy__(self, memo):
        return GtOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return GtOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class GeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 >= res2

    def __deepcopy__(self, memo):
        return GeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return GeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class EqOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(EqOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 == res2

    def __deepcopy__(self, memo):
        return EqOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return EqOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class NeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(NeOperatorValueHolder, self).__init__(left, right)

    cpdef object result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()

        return res1 != res2

    def __deepcopy__(self, memo):
        return NeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return NeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class Identity(Accumulator):

    def __init__(self, value):
        self._dependency = []
        self._window = 0
        self._value = value
        self._returnSize = 1
        self._isFull = 0

    cpdef push(self, dict data):
        pass

    cpdef object result(self):
        return self._value

    def __deepcopy__(self, memo):
        return Identity(self._value)

    def __reduce__(self):
        d = {}

        return Identity, (self._value,), d

    def __setstate__(self, state):
        pass


cdef class StatelessSingleValueAccumulator(Accumulator):

    def __init__(self, dependency='x'):
        super(StatelessSingleValueAccumulator, self).__init__(dependency)
        self._returnSize = 1
        self._window = 0

    cdef _push(self, dict data):
        if not self._isValueHolderContained:
            try:
                value = data[self._dependency]
            except KeyError:
                value = np.nan
        else:
            self._dependency.push(data)
            value = self._dependency.result()
        return value

    def __deepcopy__(self, memo):
        return StatelessSingleValueAccumulator(self._dependency)

    def __reduce__(self):
        d = {}

        return StatelessSingleValueAccumulator, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Latest(StatelessSingleValueAccumulator):

    def __init__(self, dependency='x'):
        super(Latest, self).__init__(dependency)
        self._window = 0
        self._returnSize = 1
        self._latest = np.nan

    cpdef push(self, dict data):
        value = self._push(data)
        if isnan(value):
            return np.nan
        self._isFull = 1
        self._latest = value

    cpdef object result(self):
        return self._latest

    def __deepcopy__(self, memo):
        return Latest(self._dependency)

    def __reduce__(self):
        d = {}

        return Latest, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef int isanumber(a):
    cdef int bool_a = 1
    try:
        float(repr(a))
    except:
        bool_a = 0

    return bool_a


cpdef build_holder(name):
    if isinstance(name, Accumulator):
        return deepcopy(name)
    elif isinstance(name, str):
        return Latest(name)
    elif isanumber(name):
        return Identity(float(name))
    elif hasattr(name, '__iter__'):
        return build_holder(name[0])


cdef class CompoundedValueHolder(Accumulator):

    def __init__(self, left, right):
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._returnSize = self._right.valueSize
        self._window = self._left.window + self._right.window - 1
        self._dependency = deepcopy(self._left.dependency)

        if hasattr(right.dependency, '__iter__'):
            pyFinAssert(left.valueSize == len(right.dependency), ValueError, "left value size {0} "
                                                                          "should be equal to right dependency size {1}"
                     .format(left.valueSize, len(right.dependency)))
        else:
            pyFinAssert(left.valueSize == 1, ValueError, "left value size {0} should be equal to right dependency size 1"
                     .format(left.valueSize))

    cpdef push(self, dict data):
        self._left.push(data)
        values = self._left.result()
        if not hasattr(values, '__iter__'):
            parameters = {self._right.dependency: values}
        else:
            parameters = {name: value for name, value in zip(self._right.dependency, values)}
        self._right.push(parameters)

    cpdef object result(self):
        return self._right.result()

    cpdef int isFull(self):
        if self._left.isFull() and self._right.isFull():
            return 1
        else:
            return 0

    def __deepcopy__(self, memo):
        return CompoundedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}

        return CompoundedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class IIF(Accumulator):

    def __init__(self, cond, left, right):
        self._cond = build_holder(cond)
        self._returnSize = self._cond.valueSize
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(self._cond.dependency).union(set(self._cond.dependency).union(set(self._cond.dependency))))
        self._window = max(self._cond.window, self._left.window, self._right.window)
        self._isFull = 0

    cpdef push(self, dict data):
        self._cond.push(data)
        self._left.push(data)
        self._right.push(data)
        if self._isFull == 0 and self._cond.isFull() and self._left.isFull() and self._right.isFull():
            self._isFull = 1

    cpdef object result(self):
        return self._left.result() if self._cond.result() else self._right.result()

    def __deepcopy__(self, memo):
        return IIF(self._cond, self._left, self._right)

    def __reduce__(self):
        d = {}

        return IIF, (self._cond, self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class BasicFunction(Accumulator):

    def __init__(self, dependency):
        super(BasicFunction, self).__init__(dependency)
        if self._isValueHolderContained:
            self._window = self._dependency.window
        else:
            self._window = 1
        self._returnSize = 1
        self._isFull = 0
        self._origValue = np.nan

    cpdef push(self, dict data):

        cdef double value = self.extract(data)
        if isnan(value):
            return np.nan
        self._origValue = value
        self._isFull = 1

    def __deepcopy__(self, memo):
        return BasicFunction(self._dependency)

    def __reduce__(self):
        d = {}

        return BasicFunction, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Exp(BasicFunction):
    def __init__(self, dependency):
        super(Exp, self).__init__(dependency)

    cpdef object result(self):
        return exp(self._origValue)

    def __deepcopy__(self, memo):
        return Exp(self._dependency)

    def __reduce__(self):
        d = {}

        return Exp, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Log(BasicFunction):
    def __init__(self, dependency):
        super(Log, self).__init__(dependency)

    cpdef object result(self):
        return log(self._origValue)

    def __deepcopy__(self, memo):
        return Log(self._dependency)

    def __reduce__(self):
        d = {}

        return Log, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Sqrt(BasicFunction):
    def __init__(self, dependency):
        super(Sqrt, self).__init__(dependency)

    cpdef object result(self):
        return sqrt(self._origValue)

    def __deepcopy__(self, memo):
        return Sqrt(self._dependency)

    def __reduce__(self):
        d = {}

        return Sqrt, (self._dependency,), d

    def __setstate__(self, state):
        pass


# due to the fact that pow function is much slower than ** operator
cdef class Pow(BasicFunction):

    def __init__(self, dependency, n):
        super(Pow, self).__init__(dependency)
        self._n = n

    cpdef object result(self):
        return self._origValue ** self._n

    def __deepcopy__(self, memo):
        return Pow(self._dependency, self._n)

    def __reduce__(self):
        d = {}

        return Pow, (self._dependency, self._n), d

    def __setstate__(self, state):
        pass


cdef class Abs(BasicFunction):
    def __init__(self, dependency):
        super(Abs, self).__init__(dependency)

    cpdef object result(self):
        return fabs(self._origValue)

    def __deepcopy__(self, memo):
        return Abs(self._dependency)

    def __reduce__(self):
        d = {}

        return Abs, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef double sign(double x):
    if x > 0.:
        return 1.
    elif x < 0.:
        return -1.
    else:
        return 0.


cdef class Sign(BasicFunction):
    def __init__(self, dependency):
        super(Sign, self).__init__(dependency)

    cpdef object result(self):
        return sign(self._origValue)

    def __deepcopy__(self, memo):
        return Sign(self._dependency)

    def __reduce__(self):
        d = {}

        return Sign, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Acos(BasicFunction):
    def __init__(self, dependency):
        super(Acos, self).__init__(dependency)

    cpdef object result(self):
        return acos(self._origValue)

    def __deepcopy__(self, memo):
        return Acos(self._dependency)

    def __reduce__(self):
        d = {}

        return Acos, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Acosh(BasicFunction):
    def __init__(self, dependency):
        super(Acosh, self).__init__(dependency)

    cpdef object result(self):
        return acosh(self._origValue)

    def __deepcopy__(self, memo):
        return Acosh(self._dependency)

    def __reduce__(self):
        d = {}

        return Acosh, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Asin(BasicFunction):
    def __init__(self, dependency):
        super(Asin, self).__init__(dependency)

    cpdef object result(self):
        return asin(self._origValue)

    def __deepcopy__(self, memo):
        return Asin(self._dependency)

    def __reduce__(self):
        d = {}

        return Asin, (self._dependency,), d

    def __setstate__(self, state):
        pass


cdef class Asinh(BasicFunction):
    def __init__(self, dependency):
        super(Asinh, self).__init__(dependency)

    cpdef object result(self):
        return asinh(self._origValue)

    def __deepcopy__(self, memo):
        return Asinh(self._dependency)

    def __reduce__(self):
        d = {}

        return Asinh, (self._dependency,), d

    def __setstate__(self, state):
        pass
