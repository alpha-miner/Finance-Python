# -*- coding: utf-8 -*-
u"""
Created on 2015-8-7

@author: cheng.li
"""

import copy
import sys
import operator
import six
import numpy as np
cimport numpy as np
import pandas as pd
cimport cython
from libc.math cimport isnan
from PyFin.Analysis.SeriesValues cimport SeriesValues
from PyFin.Utilities.Tools import to_dict
from PyFin.Math.Accumulators.StatefulAccumulators cimport Shift
from PyFin.Math.Accumulators.IAccumulators cimport Latest
from PyFin.Math.Accumulators.IAccumulators cimport isanumber
from PyFin.Math.MathConstants cimport NAN

if sys.version_info > (3, 0, 0):
    div_attr = "truediv"
else:
    div_attr = "div"


cdef class SecurityValueHolder(object):

    def __init__(self):
        self._window = 0
        self._holderTemplate = None
        self.updated = 0
        self.cached = None
        self._innerHolders = {}
        self._compHolder = None

    @property
    def symbolList(self):
        return list(self._innerHolders.keys())

    @property
    def fields(self):
        return self._dependency

    @property
    def window(self):
        return self._window

    cpdef push(self, dict data):

        cdef SeriesValues sec_values
        cdef Accumulator holder
        cdef str dummy_name
        self.updated = 0

        if self._compHolder:
            dummy_name = str(self._compHolder)
            self._compHolder.push(data)
            sec_values = self._compHolder.value_all()

            for name in sec_values.index():
                try:
                    holder = self._innerHolders[name]
                    holder.push({dummy_name: sec_values[name]})
                except KeyError:
                    holder = copy.deepcopy(self._holderTemplate)
                    holder.push({dummy_name:  sec_values[name]})
                    self._innerHolders[name] = holder
        else:
            for name in data:
                try:
                    holder = self._innerHolders[name]
                    holder.push(data[name])
                except KeyError:
                    holder = copy.deepcopy(self._holderTemplate)
                    holder.push(data[name])
                    self._innerHolders[name] = holder

    @property
    def value(self):
        return self.value_all()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef value_all(self):

        cdef np.ndarray[double, ndim=1] values
        cdef Accumulator holder
        cdef size_t n
        cdef int i

        if self.updated:
            return SeriesValues(self.cached.values, self.cached.name_mapping)
        else:
            keys = sorted(self._innerHolders.keys())
            n = len(keys)
            values = np.zeros(n)
            for i, name in enumerate(keys):
                try:
                    holder = self._innerHolders[name]
                    values[i] = holder.result()
                except ArithmeticError:
                    values[i] = NAN
            self.cached = SeriesValues(values, index=keys)
            self.updated = 1
            return self.cached

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SeriesValues value_by_names(self, list names):
        cdef Accumulator holder
        cdef np.ndarray[double, ndim=1] res
        cdef int i
        cdef size_t n

        if self.updated:
            return self.cached[names]
        else:
            n = len(names)
            res = np.zeros(n)
            for i, name in enumerate(names):
                holder = self._innerHolders[name]
                res[i] = holder.result()
            return SeriesValues(res, index=names)

    cpdef double value_by_name(self, name):
        cdef Accumulator holder
        if self.updated:
            return self.cached[name]
        else:
            holder = self._innerHolders[name]
            return holder.result()

    @property
    def holders(self):
        return self._innerHolders

    def isFullByName(self, name):
        return self._innerHolders[name].isFull()

    @property
    def isFull(self):
        for name in self._innerHolders:
            if not self._innerHolders[name].isFull():
                return False
        return True

    def __getitem__(self, filter):
        if isinstance(filter, SecurityValueHolder):
            return FilteredSecurityValueHolder(self, filter)
        elif isinstance(filter, int):
            return SecurityShiftedValueHolder(self, filter)
        else:
            return self.value_all()[filter]

    def __add__(self, right):
        return SecurityAddedValueHolder(self, right)

    def __sub__(self, right):
        return SecuritySubbedValueHolder(self, right)

    def __mul__(self, right):
        return SecurityMultipliedValueHolder(self, right)

    def __div__(self, right):
        return SecurityDividedValueHolder(self, right)

    def __truediv__(self, right):
        return SecurityDividedValueHolder(self, right)

    def __richcmp__(self, right, int op):

        if op == 0:
            return SecurityLtOperatorValueHolder(self, right)
        elif op == 1:
            return SecurityLeOperatorValueHolder(self, right)
        elif op == 2:
            return SecurityEqOperatorValueHolder(self, right)
        elif op == 3:
            return SecurityNeOperatorValueHolder(self, right)
        elif op == 4:
            return SecurityGtOperatorValueHolder(self, right)
        elif op == 5:
            return SecurityGeOperatorValueHolder(self, right)

    def __neg__(self):
        return SecurityNegValueHolder(self)

    def __invert__(self):
        return SecurityInvertValueHolder(self)

    def __and__(self, right):
        return SecurityAndOperatorValueHolder(self, right)

    def __rand__(self, left):
        return SecurityAndOperatorValueHolder(left, self)

    def __or__(self, right):
        return SecurityOrOperatorValueHolder(self, right)

    def __ror__(self, left):
        return SecurityOrOperatorValueHolder(left, self)

    def __xor__(self, right):
        return SecurityXorValuedHolder(self, right)

    def __rxor__(self, left):
        return SecurityXorValuedHolder(left, self)

    cpdef shift(self, int n):
        return SecurityShiftedValueHolder(self, n)

    cpdef transform(self, data, str name=None, str category_field=None, bint dropna=True):

        cdef str f
        cdef int dummy_category
        cdef np.ndarray total_category
        cdef double[:, :] matrix_values
        cdef list columns
        cdef double[:] output_values
        cdef double[:] narr_view
        cdef int j
        cdef size_t start_count
        cdef size_t end_count
        cdef list split_category
        cdef list split_values
        cdef dict dict_data

        for f in self._dependency:
            if f not in data:
                raise ValueError('({0}) dependency is not in input data'.format(f))

        dummy_category = 0
        if not category_field:
            category_field = 'dummy'
            data[category_field] = 1
            dummy_category = 1
            total_index = list(range(len(data)))
        else:
            total_index = data.index

        if not name:
            name = 'transformed'

        total_category = data[category_field].values
        data = data.select_dtypes([np.number])
        matrix_values = data.values.astype(float)
        columns = data.columns.tolist()
        split_category, split_values = to_dict(total_index, total_category.tolist(), matrix_values, columns)

        output_values = np.zeros(len(data))

        start_count = 0
        if not dummy_category:
            for j, dict_data in enumerate(split_values):
                self.push(dict_data)
                end_count = start_count + len(dict_data)
                narr_view = self.value_by_names(split_category[j]).values
                output_values[start_count:end_count]  = narr_view
                start_count = end_count
        else:
            for j, dict_data in enumerate(split_values):
                self.push(dict_data)
                output_values[j] = self.value_by_name(split_category[j][0])

        df = pd.DataFrame(np.array(output_values), index=data.index, columns=[name])
        if not dummy_category:
            df[category_field] = total_category

        if dropna:
            df.dropna(inplace=True)

        return df


cdef class FilteredSecurityValueHolder(SecurityValueHolder):

    def __init__(self, computer, filtering):
        super(FilteredSecurityValueHolder, self).__init__()
        self._filter = copy.deepcopy(filtering)
        self._computer = copy.deepcopy(computer)
        self._window = max(computer.window, filtering.window)
        self._dependency = list(set(self._computer.fields + self._filter.fields))
        self.updated = 0
        self.cached = None

    def isFullByName(self, name):
        return self._computer.isFullByName(name)

    @property
    def isFull(self):
        return self._computer.isFull

    @property
    def symbolList(self):
        return self._computer.symbolList

    @property
    def holders(self):
        return self._computer.holders

    cpdef value_all(self):
        cdef SeriesValues filter_value

        if self.updated:
            return self.cached
        else:
            filter_value = self._filter.value_all()
            self.cached = self._computer.value_all().mask(filter_value.values)
            self.updated = 1
            return self.cached

    cpdef double value_by_name(self, name):

        cdef double filter_value

        if self.updated:
            return self.cached[name]
        else:
            filter_value = self._filter.value_by_name(name)
            if filter_value:
                return self._computer.value_by_name(name)
            else:
                return NAN

    cpdef SeriesValues value_by_names(self, list names):

        cdef SeriesValues filter_value
        cdef SeriesValues orig_values

        if self.updated:
            return self.cached[names]
        else:
            filter_value = self._filter.value_by_names(names)
            orig_values = self._computer.value_by_names(names)
            return SeriesValues(np.where(filter_value.values, orig_values.values, NAN), filter_value.name_mapping)

    cpdef push(self, dict data):
        self._computer.push(data)
        self._filter.push(data)
        self.updated = 0


cdef class IdentitySecurityValueHolder(SecurityValueHolder):

    def __init__(self, value):
        super(IdentitySecurityValueHolder, self).__init__()
        self._value = value
        self._dependency = []
        self._symbols = set()

    def __str__(self):
        return str(self._value)

    def isFullByName(self, name):
        return True

    @property
    def isFull(self):
        return True

    cpdef push(self, dict data):
        self._symbols = self._symbols.union(data.keys())

    cpdef SeriesValues value_all(self):
        return SeriesValues({n: self._value for n in self._symbols})

    cpdef double value_by_name(self, name):
        return self._value

    cpdef SeriesValues value_by_names(self, list names):
        return SeriesValues({n: self._value for n in names})


cdef class SecurityConstArrayValueHolder(SecurityValueHolder):

    def __init__(self, values):
        super(SecurityConstArrayValueHolder, self).__init__()
        self._dependency = []

        if isinstance(values, SeriesValues):
            self._values = values
        else:
            self._values = SeriesValues(values)

    def isFullByName(self, name):
        return True

    @property
    def isFull(self):
        return True

    cpdef push(self, dict data):
        pass

    cpdef double value_by_name(self, name):
        if name in self._values:
            return self._values[name]
        else:
            return NAN

    cpdef SeriesValues value_by_names(self, list names):
        return self._values[names]

    cpdef SeriesValues value_all(self):
        return self._values


cdef class SecurityUnitoryValueHolder(SecurityValueHolder):

    def __init__(self, right, op):
        super(SecurityUnitoryValueHolder, self).__init__()
        self._right = copy.deepcopy(right)

        self._window = self._right.window
        self._dependency = copy.deepcopy(self._right.fields)
        self._op = op
        self.updated = 0
        self.cached = None

    def isFullByName(self, name):
        return self._right.isFullByName(name)

    @property
    def isFull(self):
        return self._right.isFull

    @property
    def symbolList(self):
        return self._right.symbolList

    cpdef push(self, dict data):
        self._right.push(data)
        self.updated = 0

    cpdef SeriesValues value_all(self):
        if self.updated:
            return self.cached
        else:
            self.cached = self._op(self._right.value_all())
            self.updated = 1
            return self.cached

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            return self._op(self._right.value_by_name(name))

    cpdef SeriesValues value_by_names(self, list names):
        if self.updated:
            return self.cached[names]
        else:
            return self._op(self._right.value_by_names(names))


cdef class SecurityNegValueHolder(SecurityUnitoryValueHolder):
    def __init__(self, right):
        super(SecurityNegValueHolder, self).__init__(
            right, operator.neg)

    def __str__(self):
        return "-{0}".format(str(self._right))


cdef class SecurityInvertValueHolder(SecurityUnitoryValueHolder):
    def __init__(self, right):
        super(SecurityInvertValueHolder, self).__init__(
            right, operator.invert)


cdef class SecurityLatestValueHolder(SecurityValueHolder):
    def __init__(self, x):
        super(SecurityLatestValueHolder, self).__init__()
        self._dependency = [x]
        self._symbol_values = {}
        self._holderTemplate = Latest(x)

    @property
    def symbolList(self):
        return list(self._symbol_values.keys())

    cpdef push(self, dict data):
        cdef double value
        cdef dict data_pack
        field = self._dependency[0]
        self.updated = 0

        for name in data:
            data_pack = data[name]
            if field in data_pack:
                value = data_pack[field]
                self._symbol_values[name] = value

            if name not in self._symbol_values:
                self._symbol_values[name] = NAN

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SeriesValues value_all(self):

        cdef np.ndarray values
        cdef size_t n
        cdef int i

        if self.updated:
            return SeriesValues(self.cached.values, self.cached.name_mapping)
        else:
            keys = sorted(self._symbol_values.keys())
            n = len(keys)
            values = np.zeros(n)
            for i, name in enumerate(keys):
                values[i] = self._symbol_values[name]
            self.cached = SeriesValues(values, index=keys)
            self.updated = 1
            return self.cached

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef SeriesValues value_by_names(self, list names):
        cdef Accumulator holder
        cdef np.ndarray res
        cdef int i
        cdef size_t n

        if self.updated:
            return self.cached[names]
        else:
            n = len(names)
            res = np.zeros(n)
            for i, name in enumerate(names):
                res[i] = self._symbol_values[name]
            return SeriesValues(res, index=names)

    cpdef double value_by_name(self, name):
        cdef Accumulator holder
        if self.updated:
            return self.cached[name]
        else:
            return self._symbol_values[name]

    def isFullByName(self, name):
        return True

    @property
    def isFull(self):
        return True

    def __str__(self):
        return str(self._holderTemplate)


cpdef SecurityValueHolder build_holder(name):
    if isinstance(name, SecurityValueHolder):
        return copy.deepcopy(name)
    elif isinstance(name, six.string_types):
        return SecurityLatestValueHolder(name)
    elif isanumber(name):
        return IdentitySecurityValueHolder(float(name))
    else:
        raise ValueError("{0} is not recognized as valid holder or name".format(name))


cdef class SecurityCombinedValueHolder(SecurityValueHolder):

    def __init__(self, left, right, op):
        super(SecurityCombinedValueHolder, self).__init__()
        self._left = build_holder(left)
        self._right = build_holder(right)

        self._window = max(self._left.window, self._right.window)
        self._dependency = list(set(self._left.fields + self._right.fields))
        self._op = op
        self.updated = 0
        self.cached = None

    def isFullByName(self, name):
        return self._left.isFullByName(name) and self._right.isFullByName(name)

    @property
    def isFull(self):
        return self._left.isFull and self._right.isFull

    @property
    def symbolList(self):
        return list(set(self._left.symbolList + self._right.symbolList))

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        self.updated = 0

    cpdef SeriesValues value_all(self):
        if self.updated:
            return self.cached
        else:
            self.cached = self._op(self._left.value_all(), self._right.value_all())
            self.updated = 1
            return self.cached

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            return self._op(self._left.value_by_name(name), self._right.value_by_name(name))

    cpdef SeriesValues value_by_names(self, list names):
        if self.updated:
            return self.cached[names]
        else:
            return self._op(self._left.value_by_names(names), self._right.value_by_names(names))


cdef class SecurityXorValuedHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityXorValuedHolder, self).__init__(
            left, right, operator.xor)

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            return self._left.value_by_name(name), self._right.value_by_name(name)

    def __str__(self):
        return "({0}, {1})".format(str(self._left), str(self._right))


cdef class SecurityAddedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityAddedValueHolder, self).__init__(
            left, right, operator.add)

    def __str__(self):
        return "{0} + {1}".format(str(self._left), str(self._right))


cdef class SecuritySubbedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecuritySubbedValueHolder, self).__init__(
            left, right, operator.sub)

    def __str__(self):
        return "{0} - {1}".format(str(self._left), str(self._right))


cdef class SecurityMultipliedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityMultipliedValueHolder, self).__init__(
            left, right, operator.mul)

    def __str__(self):

        if isinstance(self._left, (SecurityAddedValueHolder, SecuritySubbedValueHolder)):
            s1 = "({0})".format(str(self._left))
        else:
            s1 = "{0}".format(str(self._left))

        if isinstance(self._right,  (SecurityAddedValueHolder, SecuritySubbedValueHolder)):
            s2 = "({0})".format(str(self._right))
        else:
            s2 = "{0}".format(str(self._right))

        return "{0} \\times {1}".format(s1, s2)


cdef class SecurityDividedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityDividedValueHolder, self).__init__(
            left, right, getattr(operator, div_attr))

    def __str__(self):
        return "\\frac{{{0}}}{{{1}}}".format(str(self._left), str(self._right))


cdef class SecurityLtOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityLtOperatorValueHolder, self).__init__(
            left, right, operator.lt)

    def __str__(self):
        return "{0} \\lt {1}".format(str(self._left), str(self._right))


cdef class SecurityLeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityLeOperatorValueHolder, self).__init__(
            left, right, operator.le)

    def __str__(self):
        return "{0} \\le {1}".format(str(self._left), str(self._right))


cdef class SecurityGtOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityGtOperatorValueHolder, self).__init__(
            left, right, operator.gt)

    def __str__(self):
        return "{0} \\gt {1}".format(str(self._left), str(self._right))


cdef class SecurityGeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityGeOperatorValueHolder, self).__init__(
            left, right, operator.ge)

    def __str__(self):
        return "{0} \\ge {1}".format(str(self._left), str(self._right))


cdef class SecurityEqOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityEqOperatorValueHolder, self).__init__(
            left, right, operator.eq)

    def __str__(self):
        return "{0} == {1}".format(str(self._left), str(self._right))


cdef class SecurityNeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityNeOperatorValueHolder, self).__init__(
            left, right, operator.ne)

    def __str__(self):
        return "{0} \\neq {1}".format(str(self._left), str(self._right))


cdef class SecurityAndOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityAndOperatorValueHolder, self).__init__(
            left, right, operator.__and__)

    def __str__(self):
        return "{0} \\& {1}".format(str(self._left), str(self._right))


cdef class SecurityOrOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityOrOperatorValueHolder, self).__init__(
            left, right, operator.__or__)

    def __str__(self):
        return "{0} | {1}".format(str(self._left), str(self._right))


cdef class SecurityShiftedValueHolder(SecurityValueHolder):

    def __init__(self, right, n):
        super(SecurityShiftedValueHolder, self).__init__()

        self._compHolder = build_holder(right)
        self._window = self._compHolder.window + n
        self._dependency = copy.deepcopy(self._compHolder.fields)
        self._holderTemplate = Shift(Latest(str(self._compHolder)), n)

        self._innerHolders = {
            name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
        }

    def __str__(self):
        return "\\mathrm{{Shift}}({0}, {1})".format(str(self._compHolder), self._holderTemplate.lag())


cdef class SecurityIIFValueHolder(SecurityValueHolder):

    def __init__(self, flag, left, right):
        super(SecurityIIFValueHolder, self).__init__()
        self._flag = build_holder(flag)
        self._left = build_holder(left)
        self._right = build_holder(right)

        self._window = max(self._flag.window, self._left.window, self._right.window)
        self._dependency = list(set(self._flag.fields + self._left.fields + self._right.fields))
        self.updated = 0
        self.cached = None

    def isFullByName(self, name):
        return self._flag.isFullByName(name) and self._left.isFullByName(name) and self._right.isFullByName(name)

    @property
    def isFull(self):
        return self._flag.isFull and self._left.isFull and self._right.isFull

    @property
    def symbolList(self):
        return self._flag.symbolList

    cpdef push(self, dict data):
        self._flag.push(data)
        self._left.push(data)
        self._right.push(data)
        self.updated = 0

    cpdef SeriesValues value_all(self):

        cdef SeriesValues flag_value

        if self.updated:
            return self.cached
        else:
            flag_value = self._flag.value_all()

            left_value = self._left.value_all().values
            right_value = self._right.value_all().values

            self.cached = SeriesValues(np.where(flag_value.values,
                                                left_value,
                                                right_value),
                                       flag_value.name_mapping)
            self.updated = 1
            return self.cached

    cpdef double value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            if self._flag.value_by_name(name):
                return self._left.value_by_name(name)
            else:
                return self._right.value_by_name(name)

    cpdef SeriesValues value_by_names(self, list names):

        cdef SeriesValues flag_value

        if self.updated:
            return self.cached[names]
        else:

            flag_value = self._flag.value_by_names(names)

            left_value = self._left.value_by_names(names).values
            right_value = self._right.value_by_names(names).values

            return SeriesValues(np.where(flag_value.values,
                                         left_value,
                                         right_value),
                                flag_value.name_mapping)
