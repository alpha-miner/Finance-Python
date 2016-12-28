# -*- coding: utf-8 -*-
u"""
Created on 2015-8-7

@author: cheng.li
"""

from abc import ABCMeta
import copy
from collections import defaultdict
import sys
import operator
import numpy as np
import pandas as pd
from pandas import Series as SecuritiesValues
from PyFin.Utilities import to_dict
from PyFin.Math.Accumulators.StatefulAccumulators import Shift
from PyFin.Math.Accumulators.StatelessAccumulators import Latest
from PyFin.Math.Accumulators.IAccumulators import Identity

if sys.version_info > (3, 0, 0):
    div_attr = "truediv"
else:
    div_attr = "div"


class SecurityValueHolder(object):
    __metaclass__ = ABCMeta

    def __init__(self, dependency='x'):
        self._symbolList = set()
        if isinstance(dependency, SecurityValueHolder):
            self._dependency = dependency._dependency
            self._compHolder = copy.deepcopy(dependency)
            self._window = self._compHolder._window
            self._symbolList = copy.deepcopy(dependency._symbolList)
        else:
            self._compHolder = None
            if not isinstance(dependency, str) and len(dependency) == 1:
                self._dependency = [dependency[0].lower()]

            elif not isinstance(dependency, str) and len(dependency) >= 1:
                self._dependency = [name.lower() for name in dependency]
            else:
                self._dependency = [dependency.lower()]
            self._window = 0
        self._returnSize = 1
        self._holderTemplate = None

    @property
    def symbolList(self):
        return copy.deepcopy(self._symbolList)

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

    def push(self, data):

        if self._compHolder:
            self._compHolder.push(data)
            data = self._compHolder.value

            for name in data.index:
                try:
                    self.holders[name].push({'x': data[name]})
                except KeyError:
                    self._symbolList.add(name)
                    self.holders[name] = copy.deepcopy(self._holderTemplate)
                    self.holders[name].push({'x':  data[name]})

        else:
            for name in data:
                try:
                    self.holders[name].push(data[name])
                except KeyError:
                    self._symbolList.add(name)
                    self.holders[name] = copy.deepcopy(self._holderTemplate)
                    self.holders[name].push(data[name])

    @property
    def value(self):
        res = {}
        for name in self.holders:
            try:
                res[name] = self.holders[name].value
            except ArithmeticError:
                res[name] = np.nan
        return SecuritiesValues(res)

    @property
    def holders(self):
        return self._innerHolders

    def isFullByName(self, name):
        return self.holders[name].isFull

    @property
    def isFull(self):
        for name in self.holders:
            if not self.holders[name].isFull:
                return False
        return True

    def __getitem__(self, item):
        return self.value[item]

    def __add__(self, right):
        return SecurityAddedValueHolder(self, right)

    def __radd__(self, left):
        return SecurityAddedValueHolder(self, left)

    def __sub__(self, right):
        return SecuritySubbedValueHolder(self, right)

    def __rsub__(self, left):
        return SecuritySubbedValueHolder(left, self)

    def __mul__(self, right):
        return SecurityMultipliedValueHolder(self, right)

    def __rmul__(self, left):
        return SecurityMultipliedValueHolder(self, left)

    def __div__(self, right):
        return SecurityDividedValueHolder(self, right)

    def __rdiv__(self, left):
        return SecurityDividedValueHolder(left, self)

    def __truediv__(self, right):
        return SecurityDividedValueHolder(self, right)

    def __rtruediv__(self, left):
        return SecurityDividedValueHolder(left, self)

    def __lt__(self, right):
        return SecurityLtOperatorValueHolder(self, right)

    def __le__(self, right):
        return SecurityLeOperatorValueHolder(self, right)

    def __gt__(self, right):
        return SecurityGtOperatorValueHolder(self, right)

    def __ge__(self, right):
        return SecurityGeOperatorValueHolder(self, right)

    def __eq__(self, right):
        return SecurityEqOperatorValueHolder(self, right)

    def __ne__(self, right):
        return SecurityNeOperatorValueHolder(self, right)

    def __neg__(self):
        return SecurityNegValueHolder(self)

    def shift(self, n):
        return SecurityShiftedValueHolder(self, n)

    def transform(self, data, name=None, category_field=None):
        data = data.copy()
        dummy_category = False
        if not category_field:
            category_field = 'dummy'
            data[category_field] = 1
            dummy_category = True

        if not name:
            name = 'transformed'

        data_slice = data.set_index(category_field)
        dict_values, category = to_dict(data_slice)

        values = np.zeros((len(data_slice), 1))

        for i, dict_data in enumerate(dict_values):
            key = category[i]
            self.push_one(key, dict_data)
            values[i, 0] = self.__getitem__(key)

        df = pd.DataFrame(values, index=category, columns=[name])

        if dummy_category:
            df.index = data.index
            return df
        else:
            df[category_field] = df.index
            df.index = data.index
            return df


class RankedSecurityValueHolder(SecurityValueHolder):

    def __init__(self, innerValue):
        if isinstance(innerValue, SecurityValueHolder):
            self._inner = copy.deepcopy(innerValue)
        else:
            # TODO: make the rank value holder workable for a symbol
            raise ValueError("Currently only value holder input is allowed for rank holder.")
        self._window = self._inner.window
        self._returnSize = self._inner.valueSize
        self._dependency = copy.deepcopy(self._inner._dependency)
        self._symbolList = self._inner._symbolList

    @property
    def value(self):
        raw_values = self._inner.value
        return raw_values.rank(ascending=False)

    @property
    def holders(self):
        return self._inner.holders

    def push(self, data):
        self._inner.push(data)


class FilteredSecurityValueHolder(SecurityValueHolder):
    def __init__(self, computer, filtering):
        self._filter = copy.deepcopy(filtering)
        self._computer = copy.deepcopy(computer)
        self._window = max(computer.window, filtering.window)
        self._returnSize = computer.valueSize
        self._dependency = _merge2set(
            self._computer._dependency,
            self._filter._dependency
        )
        self._symbolList = self._computer._symbolList
        self._updated = False
        self._cachedFlag = None

    @property
    def holders(self):
        return self._computer.holders

    @property
    def value(self):
        filter_value = self._filter.value
        return self._computer.value[filter_value != 0]

    def push(self, data):
        self._computer.push(data)
        self._filter.push(data)

    def __getitem__(self, item):
        return self.value[item]


class IdentitySecurityValueHolder(SecurityValueHolder):
    def __init__(self, value, n=1):
        self._value = value
        self._symbolList = set()
        self._window = 1
        self._returnSize = n
        self._dependency = []
        self._innerHolders = {}
        self._holderTemplate = Identity(value, n)

    def push(self, data):
        for name in data:
            try:
                self.holders[name].push(data)
            except KeyError:
                self._symbolList.add(name)
                self.holders[name] = copy.deepcopy(self._holderTemplate)
                self.holders[name].push(data)


class SecurityUnitoryValueHolder(SecurityValueHolder):

    def __init__(self, right, op):
        self._right = copy.deepcopy(right)
        self._symbolList = set(right.symbolList)

        self._window = self._right.window
        self._dependency = copy.deepcopy(self._right._dependency)
        self._returnSize = self._right.valueSize
        self._op = op

    def push(self, data):
        self._right.push(data)

    @property
    def value(self):
        return self._op(self._right.value)


class SecurityNegValueHolder(SecurityUnitoryValueHolder):
    def __init__(self, right):
        super(SecurityNegValueHolder, self).__init__(
            right, operator.neg)


class SecurityCombinedValueHolder(SecurityValueHolder):
    def __init__(self, left, right, op):
        if isinstance(left, SecurityValueHolder):
            self._left = copy.deepcopy(left)
            if isinstance(right, SecurityValueHolder):
                self._right = copy.deepcopy(right)
                self._symbolList = set(self._left.symbolList).union(
                    set(right.symbolList))
            else:
                self._right = IdentitySecurityValueHolder(right)
                self._symbolList = set(self._left.symbolList)
        else:
            self._left = IdentitySecurityValueHolder(left)
            self._right = copy.deepcopy(right)
            self._symbolList = set(right.symbolList)

        self._window = max(self._left.window, self._right.window)
        self._dependency = _merge2set(
            self._left._dependency, self._right._dependency)
        self._returnSize = self._left.valueSize
        self._op = op

    def push(self, data):
        self._left.push(data)
        self._right.push(data)

    @property
    def value(self):
        return self._op(self._left.value, self._right.value)


class SecurityAddedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityAddedValueHolder, self).__init__(
            left, right, operator.add)


class SecuritySubbedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecuritySubbedValueHolder, self).__init__(
            left, right, operator.sub)


class SecurityMultipliedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityMultipliedValueHolder, self).__init__(
            left, right, operator.mul)


class SecurityDividedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityDividedValueHolder, self).__init__(
            left, right, getattr(operator, div_attr))


class SecurityLtOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityLtOperatorValueHolder, self).__init__(
            left, right, operator.lt)


class SecurityLeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityLeOperatorValueHolder, self).__init__(
            left, right, operator.le)


class SecurityGtOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityGtOperatorValueHolder, self).__init__(
            left, right, operator.gt)


class SecurityGeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityGeOperatorValueHolder, self).__init__(
            left, right, operator.ge)


class SecurityEqOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityEqOperatorValueHolder, self).__init__(
            left, right, operator.eq)


class SecurityNeOperatorValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityNeOperatorValueHolder, self).__init__(
            left, right, operator.ne)


class SecurityShiftedValueHolder(SecurityValueHolder):

    def __init__(self, right, n):
        super(SecurityShiftedValueHolder, self).__init__(right)
        self._returnSize = right.valueSize
        self._symbolList = set(right.symbolList)
        self._window = right.window + n
        self._dependency = copy.deepcopy(right._dependency)
        self._holderTemplate = Shift(Latest('x'), n)

        self._innerHolders = {
            name: copy.deepcopy(self._holderTemplate) for name in self._symbolList
        }


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


def _merge2dict(left, right):
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
