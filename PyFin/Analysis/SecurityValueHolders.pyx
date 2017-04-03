# -*- coding: utf-8 -*-
u"""
Created on 2015-8-7

@author: cheng.li
"""

import copy
from collections import defaultdict
import sys
import operator
import six
import numpy as np
cimport numpy as np
import pandas as pd
cimport cython
from PyFin.Analysis.SecurityValues cimport SecurityValues
from PyFin.Utilities.Tools import to_dict
from PyFin.Math.Accumulators.StatefulAccumulators cimport Shift
from PyFin.Math.Accumulators.IAccumulators cimport Latest

if sys.version_info > (3, 0, 0):
    div_attr = "truediv"
else:
    div_attr = "div"


cdef class SecurityValueHolder(object):

    def __init__(self, dependency='x'):
        if isinstance(dependency, SecurityValueHolder):
            self._dependency = dependency._dependency
            self._dependency = dependency._dependency
            self._compHolder = copy.deepcopy(dependency)
            self._window = self._compHolder._window
        else:
            self._compHolder = None
            if not isinstance(dependency, six.string_types):
                self._dependency = [name for name in dependency]
            else:
                self._dependency = [dependency]
            self._window = 0
        self._returnSize = 1
        self._holderTemplate = None
        self.updated = 0
        self.cached = None
        self._innerHolders = {}

    @property
    def symbolList(self):
        return set(self._innerHolders.keys())

    @property
    def fields(self):
        if isinstance(self._dependency, list):
            return self._dependency
        else:
            return [self._dependency]

    @property
    def valueSize(self):
        return self._returnSize

    @property
    def window(self):
        return self._window

    cpdef push(self, dict data):

        cdef SecurityValues sec_values
        cdef Accumulator holder
        self.updated = 0

        if self._compHolder:
            self._compHolder.push(data)
            sec_values = self._compHolder.value

            for name in sec_values.index():
                try:
                    holder = self._innerHolders[name]
                    holder.push({'x': sec_values[name]})
                except KeyError:
                    holder = copy.deepcopy(self._holderTemplate)
                    holder.push({'x':  sec_values[name]})
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
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def value(self):

        cdef np.ndarray values
        cdef Accumulator holder
        cdef size_t n
        cdef int i

        if self.updated:
            return SecurityValues(self.cached.values, self.cached.name_mapping)
        else:
            keys = sorted(self._innerHolders.keys())
            n = len(keys)
            values = np.empty(n, dtype='object')
            for i, name in enumerate(keys):
                try:
                    holder = self._innerHolders[name]
                    values[i] = holder.result()
                except ArithmeticError:
                    values[i] = np.nan
            self.cached = SecurityValues(values, index=keys)
            self.updated = 1
            return self.cached

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cpdef value_by_names(self, list names):
        cdef Accumulator holder
        cdef np.ndarray res
        cdef int i
        cdef size_t n

        if self.updated:
            return self.cached[names]
        else:
            n = len(names)
            res = np.empty(n, dtype='object')
            for i, name in enumerate(names):
                holder = self._innerHolders[name]
                res[i] = holder.result()
            return SecurityValues(res, index=names)

    cpdef value_by_name(self, name):
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
            return self.value[filter]

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

    cpdef copy_attributes(self, dict attributes, bint is_deep=True):
        self._dependency = copy.deepcopy(attributes['_dependency']) if is_deep else attributes['_dependency']
        self._compHolder = copy.deepcopy(attributes['_compHolder']) if is_deep else attributes['_compHolder']
        self._window = attributes['_window']
        self._returnSize = attributes['_returnSize']
        self._holderTemplate = copy.deepcopy(attributes['_holderTemplate']) if is_deep else attributes['_holderTemplate']
        self.updated = attributes['updated']
        self._innerHolders = copy.deepcopy(attributes['_innerHolders']) if is_deep else attributes['_innerHolders']
        self.cached = copy.deepcopy(attributes['cached']) if is_deep else attributes['cached']

    cpdef collect_attributes(self):
        attributes = dict()
        attributes['_dependency'] = self._dependency
        attributes['_compHolder'] = self._compHolder
        attributes['_window'] = self._window
        attributes['_returnSize'] = self._returnSize
        attributes['_holderTemplate'] = self._holderTemplate
        attributes['updated'] = self.updated
        attributes['_innerHolders'] = self._innerHolders
        attributes['cached'] = self.cached
        return attributes

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
        matrix_values = data.as_matrix().astype(float)
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
        super(FilteredSecurityValueHolder, self).__init__([])
        self._filter = copy.deepcopy(filtering)
        self._computer = copy.deepcopy(computer)
        self._window = max(computer.window, filtering.window)
        self._returnSize = computer.valueSize
        self._dependency = _merge2set(
            self._computer._dependency,
            self._filter._dependency
        )
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

    @property
    def value(self):
        cdef SecurityValues filter_value

        if self.updated:
            return self.cached
        else:
            filter_value = self._filter.value
            self.cached = self._computer.value.mask(filter_value.values)
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):

        cdef double filter_value

        if self.updated:
            return self.cached[name]
        else:
            filter_value = self._filter.value_by_name(name)
            if filter_value:
                return self._computer.value_by_name(name)
            else:
                return np.nan

    cpdef value_by_names(self, list names):

        cdef SecurityValues filter_value
        cdef SecurityValues orig_values

        if self.updated:
            return self.cached[names]
        else:
            filter_value = self._filter.value_by_names(names)
            orig_values = self._computer.value_by_names(names)
            return SecurityValues(np.where(filter_value.values, orig_values.values, np.nan), filter_value.name_mapping)

    cpdef push(self, dict data):
        self._computer.push(data)
        self._filter.push(data)
        self.updated = 0

    def __deepcopy__(self, memo):
        return FilteredSecurityValueHolder(self._computer, self._filter)

    def __reduce__(self):
        d = {}

        return FilteredSecurityValueHolder, (self._computer, self._filter), d

    def __setstate__(self, state):
        pass



cdef class IdentitySecurityValueHolder(SecurityValueHolder):

    def __init__(self, value):
        super(IdentitySecurityValueHolder, self).__init__([])
        self._value = value

    def isFullByName(self, name):
        return True

    @property
    def isFull(self):
        return True

    cpdef push(self, dict data):
        pass

    @property
    def value(self):
        return self._value

    cpdef value_by_name(self, name):
        return self._value

    cpdef value_by_names(self, list names):
        return self._value

    def __deepcopy__(self, memo):
        return IdentitySecurityValueHolder(self._value)

    def __reduce__(self):
        d = {}

        return IdentitySecurityValueHolder, (self._value,), d

    def __setstate__(self, state):
        pass


cdef class SecurityConstArrayValueHolder(SecurityValueHolder):

    def __init__(self, values):
        super(SecurityConstArrayValueHolder, self).__init__([])

        if isinstance(values, SecurityValues):
            self._values = values
        else:
            self._values = SecurityValues(values)

    def isFullByName(self, name):
        if name in self._values:
            return True
        else:
            return False

    @property
    def isFull(self):
        return True

    cpdef push(self, dict data):
        pass

    cpdef value_by_name(self, name):
        if name in self._values:
            return self._values[name]
        else:
            return np.nan

    cpdef value_by_names(self, list names):
        return self._values[names]

    @property
    def value(self):
        return self._values

    def __deepcopy__(self, memo):
        return SecurityConstArrayValueHolder(self._values)

    def __reduce__(self):
        d = {}

        return SecurityConstArrayValueHolder, (self._values,), d

    def __setstate__(self, state):
        pass


cdef class SecurityUnitoryValueHolder(SecurityValueHolder):

    def __init__(self, right, op):
        super(SecurityUnitoryValueHolder, self).__init__([])
        self._right = copy.deepcopy(right)

        self._window = self._right.window
        self._dependency = copy.deepcopy(self._right._dependency)
        self._returnSize = self._right.valueSize
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

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            self.cached = self._op(self._right.value)
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            return self._op(self._right.value_by_name(name))

    cpdef value_by_names(self, list names):
        if self.updated:
            return self.cached[names]
        else:
            return self._op(self._right.value_by_names(names))


cdef class SecurityNegValueHolder(SecurityUnitoryValueHolder):
    def __init__(self, right):
        super(SecurityNegValueHolder, self).__init__(
            right, operator.neg)

    def __deepcopy__(self, memo):
        return SecurityNegValueHolder(self._right)

    def __reduce__(self):
        d = {}

        return SecurityNegValueHolder, (self._right,), d

    def __setstate__(self, state):
        pass


cdef class SecurityInvertValueHolder(SecurityUnitoryValueHolder):
    def __init__(self, right):
        super(SecurityInvertValueHolder, self).__init__(
            right, operator.invert)

    def __deepcopy__(self, memo):
        return SecurityInvertValueHolder(self._right)

    def __reduce__(self):
        d = {}

        return SecurityInvertValueHolder, (self._right,), d

    def __setstate__(self, state):
        pass


cdef class SecurityLatestValueHolder(SecurityValueHolder):
    def __init__(self, dependency='x'):
        super(SecurityLatestValueHolder, self).__init__(dependency)
        if self._compHolder:
            self._holderTemplate = Latest(dependency='x')
            self._innerHolders = {
                name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
                }
        else:
            self._holderTemplate = Latest(dependency=self._dependency)

    def __deepcopy__(self, memo):
        if self._compHolder:
            copied = SecurityLatestValueHolder(self._compHolder)
        else:
            copied = SecurityLatestValueHolder(self._dependency)

        copied.copy_attributes(self.collect_attributes(), is_deep=True)
        return copied

    def __reduce__(self):
        d = self.collect_attributes()
        if self._compHolder:
            return SecurityLatestValueHolder, (self._compHolder,), d
        else:
            return SecurityLatestValueHolder, (self._dependency,), d

    def __setstate__(self, state):
        self.copy_attributes(state, is_deep=False)


cdef class SecurityCombinedValueHolder(SecurityValueHolder):

    def __init__(self, left, right, op):
        if isinstance(left, SecurityValueHolder):
            self._left = copy.deepcopy(left)
            if isinstance(right, SecurityValueHolder):
                self._right = copy.deepcopy(right)
            else:
                self._right = IdentitySecurityValueHolder(right)
        elif isinstance(left, six.string_types):
            self._left = SecurityLatestValueHolder(left)
            self._right = copy.deepcopy(right)
        else:
            self._left = IdentitySecurityValueHolder(left)
            self._right = copy.deepcopy(right)

        self._window = max(self._left.window, self._right.window)
        self._dependency = _merge2set(
            self._left._dependency, self._right._dependency)
        self._returnSize = self._left.valueSize
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
        return self._left.symbolList.union(self._right.symbolList)

    cpdef push(self, dict data):
        self._left.push(data)
        self._right.push(data)
        self.updated = 0

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            self.cached = self._op(self._left.value, self._right.value)
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            return self._op(self._left.value_by_name(name), self._right.value_by_name(name))

    cpdef value_by_names(self, list names):
        if self.updated:
            return self.cached[names]
        else:
            return self._op(self._left.value_by_names(names), self._right.value_by_names(names))

    def __deepcopy__(self, memo):
        return SecurityCombinedValueHolder(self._left, self._right, self._op)


cdef class SecurityAddedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityAddedValueHolder, self).__init__(
            left, right, operator.add)

    def __deepcopy__(self, memo):
        return SecurityAddedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityAddedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecuritySubbedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecuritySubbedValueHolder, self).__init__(
            left, right, operator.sub)

    def __deepcopy__(self, memo):
        return SecuritySubbedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecuritySubbedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityMultipliedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityMultipliedValueHolder, self).__init__(
            left, right, operator.mul)

    def __deepcopy__(self, memo):
        return SecurityMultipliedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityMultipliedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityDividedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityDividedValueHolder, self).__init__(
            left, right, getattr(operator, div_attr))

    def __deepcopy__(self, memo):
        return SecurityDividedValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityDividedValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityLtOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityLtOperatorValueHolder, self).__init__(
            left, right, operator.lt)

    def __deepcopy__(self, memo):
        return SecurityLtOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityLtOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityLeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityLeOperatorValueHolder, self).__init__(
            left, right, operator.le)

    def __deepcopy__(self, memo):
        return SecurityLeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityLeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityGtOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityGtOperatorValueHolder, self).__init__(
            left, right, operator.gt)

    def __deepcopy__(self, memo):
        return SecurityGtOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityGtOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityGeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityGeOperatorValueHolder, self).__init__(
            left, right, operator.ge)

    def __deepcopy__(self, memo):
        return SecurityGeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityGeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityEqOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityEqOperatorValueHolder, self).__init__(
            left, right, operator.eq)

    def __deepcopy__(self, memo):
        return SecurityEqOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityEqOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityNeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityNeOperatorValueHolder, self).__init__(
            left, right, operator.ne)

    def __deepcopy__(self, memo):
        return SecurityNeOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityNeOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityAndOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityAndOperatorValueHolder, self).__init__(
            left, right, operator.__and__)

    def __deepcopy__(self, memo):
        return SecurityAndOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityAndOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityOrOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityOrOperatorValueHolder, self).__init__(
            left, right, operator.__or__)

    def __deepcopy__(self, memo):
        return SecurityOrOperatorValueHolder(self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityOrOperatorValueHolder, (self._left, self._right), d

    def __setstate__(self, state):
        pass


cdef class SecurityShiftedValueHolder(SecurityValueHolder):

    def __init__(self, right, n):
        super(SecurityShiftedValueHolder, self).__init__(right)
        self._returnSize = right.valueSize
        self._window = right.window + n
        self._dependency = copy.deepcopy(right._dependency)
        self._holderTemplate = Shift(Latest('x'), n)

        self._innerHolders = {
            name: copy.deepcopy(self._holderTemplate) for name in self._compHolder.symbolList
        }

    def __deepcopy__(self, memo):
        if self._compHolder:
            return SecurityShiftedValueHolder(self._compHolder, self._holderTemplate.lag())
        else:
            return SecurityShiftedValueHolder(self._dependency, self._holderTemplate.lag())

    def __reduce__(self):
        d = {}
        if self._compHolder:
            return SecurityShiftedValueHolder, (self._compHolder, self._holderTemplate.lag()), d
        else:
            return SecurityShiftedValueHolder, (self._dependency, self._holderTemplate.lag()), d

    def __setstate__(self, state):
        pass


cdef class SecurityIIFValueHolder(SecurityValueHolder):

    def __init__(self, flag, left, right):

        if not isinstance(flag, SecurityValueHolder):
            if isinstance(flag, six.string_types):
                self._flag = SecurityLatestValueHolder(flag)
            else:
                self._flag = IdentitySecurityValueHolder(flag)
        else:
            self._flag = copy.deepcopy(flag)

        if not isinstance(left, SecurityValueHolder):
            if isinstance(left, six.string_types):
                self._left = SecurityLatestValueHolder(left)
            else:
                self._left = IdentitySecurityValueHolder(left)
        else:
            self._left = copy.deepcopy(left)

        if not isinstance(right, SecurityValueHolder):
            if isinstance(left, six.string_types):
                self._right = SecurityLatestValueHolder(right)
            else:
                self._right = IdentitySecurityValueHolder(right)
        else:
            self._right = copy.deepcopy(right)

        self._window = max(self._flag.window, self._left.window, self._right.window)
        self._dependency = _merge2set(self._flag._dependency, _merge2set(
            self._left._dependency, self._right._dependency))
        self._returnSize = self._flag.valueSize
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

    @property
    def value(self):

        cdef SecurityValues flag_value

        if self.updated:
            return self.cached
        else:
            flag_value = self._flag.value

            if isinstance(self._left, IdentitySecurityValueHolder):
                left_value = self._left.value
            else:
                left_value = self._left.value.values

            if isinstance(self._right, IdentitySecurityValueHolder):
                right_value = self._right.value
            else:
                right_value = self._right.value.values

            self.cached = SecurityValues(np.where(flag_value.values,
                                                  left_value,
                                                  right_value),
                                         flag_value.name_mapping)
            self.updated = 1
            return self.cached

    cpdef value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            if self._flag.value_by_name(name):
                return self._left.value_by_name(name)
            else:
                return self._right.value_by_name(name)

    cpdef value_by_names(self, list names):

        cdef SecurityValues flag_value

        if self.updated:
            return self.cached[names]
        else:

            flag_value = self._flag.value_by_names(names)

            if isinstance(self._left, IdentitySecurityValueHolder):
                left_value = self._left.value_by_names(names)
            else:
                left_value = self._left.value_by_names(names).values

            if isinstance(self._right, IdentitySecurityValueHolder):
                right_value = self._right.value_by_names(names)
            else:
                right_value = self._right.value_by_names(names).values

            return SecurityValues(np.where(flag_value.values,
                                           left_value,
                                           right_value),
                                  flag_value.name_mapping)

    def __deepcopy__(self, memo):
        return SecurityIIFValueHolder(self._flag, self._left, self._right)

    def __reduce__(self):
        d = {}
        return SecurityIIFValueHolder, (self._flag, self._left, self._right), d

    def __setstate__(self, state):
        pass


def dependencyCalculator(*args):
    res = defaultdict(list)
    tmp = {}
    for value in args:
        tmp = _merge2dict(tmp, value)

    for name in tmp:
        if isinstance(tmp[name], list):
            for field in tmp[name]:
                res[field].append(name)
        else:
            res[tmp[name]].append(name)
    return res


# detail implementation
cdef dict _merge2dict(dict left, dict right):
    res = {}
    for name in left:
        if name in right:
            if isinstance(left[name], list):
                if isinstance(right[name], list):
                    res[name] = list(set(left[name] + right[name]))
                else:
                    res[name] = list(set(left[name] + [right[name]]))
            else:
                if isinstance(right[name], list):
                    res[name] = list(set([left[name]] + right[name]))
                else:
                    res[name] = list(set([left[name]] + [right[name]]))
        else:
            res[name] = left[name]

    for name in right:
        if name not in left:
            res[name] = right[name]
    return res


def _merge2set(left, right):
    if isinstance(left, list):
        if isinstance(right, list):
            res = list(set(left + right))
        else:
            res = list(set(left + [right]))
    else:
        if isinstance(right, list):
            res = list(set([left] + right))
        else:
            res = list(set([left] + [right]))
    return res
