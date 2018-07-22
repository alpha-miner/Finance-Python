# -*- coding: utf-8 -*-
u"""
Created on 2017-2-8

@author: cheng.li
"""

import copy
from copy import deepcopy
import six
from libc.math cimport sqrt
from libc.math cimport fabs
from libc.math cimport log
from libc.math cimport exp
from libc.math cimport acos
from libc.math cimport acosh
from libc.math cimport asin
from libc.math cimport asinh
cimport cython
import numpy as np
cimport numpy as np
import pandas as pd
from PyFin.Utilities.Asserts cimport pyFinAssert
from PyFin.Math.MathConstants cimport NAN
from PyFin.Math.udfs cimport sign


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
        elif op == 2:
            return EqOperatorValueHolder(self, right)
        elif op == 3:
            return NeOperatorValueHolder(self, right)
        elif op == 4:
            return GtOperatorValueHolder(self, right)
        elif op == 5:
            return GeOperatorValueHolder(self, right)

    def __rshift__(self, right):
        if isinstance(right, IAccumulator):
            return CompoundedValueHolder(self, right)

        try:
            return right(self)
        except TypeError:
            raise ValueError('{0} is not recognized as a valid operator'.format(right))

    def __neg__(self):
        return Negative(self)


cdef class Accumulator(IAccumulator):

    def __init__(self):
        self._isFull = False
        self._window = 0

    cpdef push(self, dict data):
        pass

    cpdef double result(self):
        pass

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef transform(self, data, str name=None, bint to_sort=False):

        cdef int i
        cdef int k
        cdef double[:, :] matrix_values
        cdef size_t n = len(data)
        cdef double[:] output_values = np.zeros(n)
        cdef list columns
        cdef size_t column_length
        cdef dict data_dict

        if to_sort:
            data.sort_index(inplace=True)

        if not name:
            name = 'transformed'

        data = data.select_dtypes([np.number])
        matrix_values = data.values.astype(float)
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

    cpdef bint isFull(self):
        return self._isFull

    @property
    def window(self):
        return self._window

    @property
    def dependency(self):
        return self._dependency


cdef class Negative(Accumulator):

    def __init__(self, x):
        super(Negative, self).__init__()
        self._window = x.window
        self._isFull = False
        self._inner = copy.deepcopy(x)
        self._dependency = self._inner.dependency

    cpdef push(self, dict data):
        self._inner.push(data)
        self._isFull = self._isFull if self._isFull else self._inner.isFull()

    def __str__(self):
        return "-{0}".format(str(self._inner))

    cpdef double result(self):
        return -self._inner.result()


cdef class CombinedValueHolder(Accumulator):

    def __init__(self, left, right):
        super(CombinedValueHolder, self).__init__()
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(self._left.dependency + self._right.dependency))
        self._window = max(self._left.window, self._right.window)
        self._isFull = False

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        self._isFull = self._isFull or (self._left.isFull() and self._right.isFull())


cdef class AddedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(AddedValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 + res2

    def __str__(self):
        return "{0} + {1}".format(str(self._left), str(self._right))


cdef class MinusedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MinusedValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 - res2

    def __str__(self):
        return "{0} - {1}".format(str(self._left), str(self._right))


cdef class MultipliedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(MultipliedValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 * res2

    def __str__(self):

        if isinstance(self._left, (AddedValueHolder, MinusedValueHolder)):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  (AddedValueHolder, MinusedValueHolder)):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \\times {1}".format(s1, s2)


cdef class DividedValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(DividedValueHolder, self).__init__(left, right)

    @cython.cdivision(True)
    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 / res2

    def __str__(self):
        return "\\frac{{{0}}}{{{1}}}".format(str(self._left), str(self._right))


cdef class LtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LtOperatorValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 < res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \lt {1}".format(s1, s2)


cdef class LeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(LeOperatorValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 <= res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \le {1}".format(s1, s2)


cdef class GtOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GtOperatorValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 > res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \gt {1}".format(s1, s2)


cdef class GeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(GeOperatorValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 >= res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \ge {1}".format(s1, s2)


cdef class EqOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(EqOperatorValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 == res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} = {1}".format(s1, s2)


cdef class NeOperatorValueHolder(CombinedValueHolder):
    def __init__(self, left, right):
        super(NeOperatorValueHolder, self).__init__(left, right)

    cpdef double result(self):
        cdef double res1 = self._left.result()
        cdef double res2 = self._right.result()
        return res1 != res2

    def __str__(self):

        if isinstance(self._left, CombinedValueHolder):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  CombinedValueHolder):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \\neq {1}".format(s1, s2)


cdef class Identity(Accumulator):

    def __init__(self, value):
        self._dependency = []
        self._window = 0
        self._value = value
        self._isFull = True

    cpdef push(self, dict data):
        pass

    cpdef double result(self):
        return self._value

    def __str__(self):
        return str(self._value)


cdef class Latest(Accumulator):

    def __init__(self, x='x', current_value=NAN):
        """
        Latest should only be used as a vanilla named value holder
        :param x:
        :param current_value:
        """
        super(Latest, self).__init__()
        self._window = 0
        self._isFull = True
        self._latest = current_value
        self._dependency = [x]

    cpdef push(self, dict data):
        try:
            self._latest = data[self._dependency[0]]
        except KeyError:
            pass

    def __str__(self):
        return "''\\text{{{0}}}''".format(str(self._dependency[0]))

    cpdef double result(self):
        return self._latest


cdef bint isanumber(a):
    cdef bint bool_a = True
    try:
        float(repr(a))
    except:
        bool_a = False

    return bool_a


cpdef build_holder(name):
    if isinstance(name, Accumulator):
        return deepcopy(name)
    elif isinstance(name, six.string_types):
        return Latest(name)
    elif isanumber(name):
        return Identity(float(name))
    elif hasattr(name, '__iter__'):
        return build_holder(name[0])


cdef class CompoundedValueHolder(Accumulator):

    def __init__(self, left, right):
        super(CompoundedValueHolder, self).__init__()
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._window = self._left.window + self._right.window
        self._dependency = deepcopy(self._left.dependency)

    cpdef push(self, dict data):
        cdef double left_value
        self._left.push(data)
        left_value = self._left.result()
        self._right.push({self._right.dependency[0]: left_value})
        self._isFull = self._isFull or (self._left.isFull() and self._right.isFull())

    cpdef double result(self):
        return self._right.result()


cdef class IIF(Accumulator):

    def __init__(self, cond, left, right):
        super(IIF, self).__init__()
        self._cond = build_holder(cond)
        self._left = build_holder(left)
        self._right = build_holder(right)
        self._dependency = list(set(self._cond.dependency + self._left.dependency + self._right.dependency))
        self._window = max(self._cond.window, self._left.window, self._right.window)
        self._isFull = False

    cpdef push(self, dict data):
        self._cond.push(data)
        self._left.push(data)
        self._right.push(data)
        self._isFull = self._isFull or (self._cond.isFull() and self._left.isFull() and self._right.isFull())

    cpdef double result(self):
        return self._left.result() if self._cond.result() else self._right.result()


cdef class BasicFunction(Accumulator):

    def __init__(self, x, orig_value=NAN):
        super(BasicFunction, self).__init__()
        self._inner = build_holder(x)
        self._window = self._inner.window
        self._isFull = False
        self._dependency = self._inner.dependency
        self._origValue = orig_value

    cpdef push(self, dict data):
        self._inner.push(data)
        self._origValue = self._inner.result()
        self._isFull = self._isFull or self._inner.isFull()


cdef class Exp(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Exp, self).__init__(x, orig_value)

    cpdef double result(self):
        return exp(self._origValue)

    def __str__(self):
        return "\\exp({0})".format(str(self._inner))


cdef class Log(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Log, self).__init__(x, orig_value)

    cpdef double result(self):
        return log(self._origValue)

    def __str__(self):
        return "\\ln({0})".format(str(self._inner))


cdef class Sqrt(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Sqrt, self).__init__(x, orig_value)

    cpdef double result(self):
        return sqrt(self._origValue)

    def __str__(self):
        return "\\sqrt{{{0}}}".format(str(self._inner))


# due to the fact that pow function is much slower than ** operator
cdef class Pow(BasicFunction):

    def __init__(self, x, n, orig_value=NAN):
        super(Pow, self).__init__(x, orig_value)
        self._n = n

    cpdef double result(self):
        return self._origValue ** self._n

    def __str__(self):
        return "{0} ^ {{{1}}}".format(str(self._inner), self._n)


cdef class Abs(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Abs, self).__init__(x, orig_value)

    cpdef double result(self):
        return fabs(self._origValue)

    def __str__(self):
        return "\\left| {0} \\right|".format(str(self._inner))


cdef class Sign(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Sign, self).__init__(x, orig_value)

    cpdef double result(self):
        return sign(self._origValue)

    def __str__(self):
        return "\\mathrm{{sign}}({0})".format(str(self._inner))


cdef class Acos(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Acos, self).__init__(x, orig_value)

    cpdef double result(self):
        return acos(self._origValue)

    def __str__(self):
        return "\\mathrm{{ACos}}({0})".format(str(self._inner))


cdef class Acosh(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Acosh, self).__init__(x, orig_value)

    cpdef double result(self):
        return acosh(self._origValue)

    def __str__(self):
        return "\\mathrm{{ACosh}}({0})".format(str(self._inner))

cdef class Asin(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Asin, self).__init__(x, orig_value)

    cpdef double result(self):
        return asin(self._origValue)

    def __str__(self):
        return "\\mathrm{{ASin}}({0})".format(str(self._inner))


cdef class Asinh(BasicFunction):
    def __init__(self, x, orig_value=NAN):
        super(Asinh, self).__init__(x, orig_value)

    cpdef double result(self):
        return asinh(self._origValue)

    def __str__(self):
        return "\\mathrm{{ASinh}}({0})".format(str(self._inner))
