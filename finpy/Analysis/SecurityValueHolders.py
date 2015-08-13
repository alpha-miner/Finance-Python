# -*- coding: utf-8 -*-
u"""
Created on 2015-8-7

@author: cheng.li
"""

from abc import ABCMeta
import copy
from collections import defaultdict
import numpy as np
from finpy.Math.Accumulators.StatefulAccumulators import Shift
from finpy.Math.Accumulators.IAccumulators import CompoundedValueHolder
from finpy.Math.Accumulators.IAccumulators import Identity
from finpy.Math.Accumulators.IAccumulators import AddedValueHolder
from finpy.Math.Accumulators.IAccumulators import MinusedValueHolder
from finpy.Math.Accumulators.IAccumulators import MultipliedValueHolder
from finpy.Math.Accumulators.IAccumulators import DividedValueHolder


class SecuritiesValues(object):

    def __init__(self, values):
        self._values = copy.deepcopy(values)

    def __getitem__(self, item):
        return self._values[item]

    def __neg__(self):
        return SecuritiesValues({
            name: -self._values[name] for name in self._values
        })

    def __iter__(self):
        return self._values.__iter__()

    def __len__(self):
        return self._values.__len__()

    def __add__(self, right):
        if isinstance(right, SecuritiesValues):
            assert self._values.keys() == right._values.keys(), "left security names {0} is not equal to right {1}" \
                                                                .format(self._values.keys(), right._values.keys())
            return SecuritiesValues(
                {
                    name: self._values[name] + right._values[name] for name in self._values
                }
            )
        else:
            return SecuritiesValues(
                {
                    name: self._values[name] + right for name in self._values
                }
            )

    def __radd__(self, left):
        return self.__add__(left)

    def __sub__(self, right):
        if isinstance(right, SecuritiesValues):
            assert self._values.keys() == right._values.keys(), "left security names {0} is not equal to right {1}" \
                                                                .format(self._values.keys(), right._values.keys())
            return SecuritiesValues(
                {
                    name: self._values[name] - right._values[name] for name in self._values
                }
            )
        else:
            return SecuritiesValues(
                {
                    name: self._values[name] - right for name in self._values
                }
            )

    def __rsub__(self, left):
        return SecuritiesValues(
            {
                name: left - self._values[name] for name in self._values
            }
        )

    def __mul__(self, right):
        if isinstance(right, SecuritiesValues):
            assert self._values.keys() == right._values.keys(), "left security names {0} is not equal to right {1}" \
                                                                .format(self._values.keys(), right._values.keys())
            return SecuritiesValues(
                {
                    name: self._values[name] * right._values[name] for name in self._values
                }
            )
        else:
            return SecuritiesValues(
                {
                    name: self._values[name] * right for name in self._values
                }
            )

    def __rmul__(self, left):
        return self.__mul__(left)

    def __div__(self, right):
        if isinstance(right, SecuritiesValues):
            assert self._values.keys() == right._values.keys(), "left security names {0} is not equal to right {1}" \
                                                                .format(self._values.keys(), right._values.keys())
            return SecuritiesValues(
                {
                    name: self._values[name] / right._values[name] for name in self._values
                }
            )
        else:
            return SecuritiesValues(
                {
                    name: self._values[name] / right for name in self._values
                }
            )

    def __rdiv__(self, left):
        return SecuritiesValues(
            {
                name: left / self._values[name] for name in self._values
            }
        )

    def __truediv__(self, right):
        return self.__div__(right)

    def __rtruediv__(self, left):
        return self.__rdiv__(left)

    def __str__(self):
        return self._values.__str__()


class SecurityValueHolder(object):

    __metaclass__ = ABCMeta

    def __init__(self, pNames='x', symbolList=None):
        if symbolList is None:
            # should do something to get a global value here
            self._symbolList = set(['600000.xshg', 'aapl', 'ibm', "msft"])
        else:
            self._symbolList = set(s.lower() for s in symbolList)
        if isinstance(pNames, SecurityValueHolder):
            self._pNames = pNames._pNames
        else:
            if not isinstance(pNames, str) and len(pNames) == 1:
                self._pNames = pNames[0].lower()
            elif not isinstance(pNames, str) and len(pNames) >= 1:
                self._pNames = [name.lower() for name in pNames]
            else:
                self._pNames = pNames.lower()
        self._window = 1
        self._returnSize = 1

    @property
    def symbolList(self):
        return list(self._symbolList)

    @property
    def dependency(self):
        return {
            symbol: self._pNames for symbol in self._symbolList
        }

    @property
    def valueSize(self):
        return self._returnSize

    @property
    def window(self):
        return self._window

    def push(self, data):
        names = set(self._symbolList).intersection(set(data.keys()))
        for name in names:
            self._innerHolders[name].push(**data[name])

    @property
    def value(self):
        res = {}
        for name in self._innerHolders:
            try:
                res[name] = self._innerHolders[name].value
            except:
                res[name] = np.nan
        return SecuritiesValues(res)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            res = copy.deepcopy(self)
            res._symbolList = set(i.lower() for i in item)
            assert len(res._symbolList) == len(item), "security name can't be duplicated"
            res._innerHolders = \
                {
                    name: self._innerHolders[name] for name in res._symbolList
                }
            return res
        elif item.lower() in self._innerHolders:
            item = item.lower()
            res = copy.deepcopy(self)
            res._symbolList = set([item])
            assert len(res._symbolList) == len([item]), "security name can't be duplicated"
            res._innerHolders = \
                {
                    name: self._innerHolders[name] for name in res._symbolList
                }
            return res
        else:
            raise TypeError("{0} is not a valid index".format(item))

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


class IdentitySecurityValueHolder(SecurityValueHolder):

    def __init__(self, value, n=1):
        self._value = value
        self._symbolList = []
        self._window = 1
        self._returnSize = n
        self._pNames = []
        self._innerHolders = {
            'wildCard': Identity(value, n)
        }

    def push(self, data):
        if len(self._pNames) != 0:
            self._innerHolders['wildCard'].push(**data)

    @property
    def value(self):
        return self._innerHolders['wildCard'].value


class SecurityCombinedValueHolder(SecurityValueHolder):

    def __init__(self, left, right, HolderType):
        if isinstance(left, SecurityValueHolder):
            self._left = copy.deepcopy(left)
            if isinstance(right, SecurityValueHolder):
                self._right = copy.deepcopy(right)
                self._symbolList = set(self._left._symbolList).union(set(right._symbolList))
            else:
                self._right = IdentitySecurityValueHolder(right)
                self._symbolList = set(self._left._symbolList)
        else:
            self._left = IdentitySecurityValueHolder(left)
            self._right = copy.deepcopy(right)
            if isinstance(right, SecurityValueHolder):
                self._symbolList = set(self._left._symbolList).union(set(right._symbolList))
            else:
                self._symbolList = set(self._left._symbolList)

        self._window = max(self._left.window, self._right.window)
        self._pNames = list(set(self._left._pNames).union(set(self._right._pNames)))
        self._returnSize = self._left.valueSize

        if len(self._right.symbolList) == 0:
            self._innerHolders = {
                name: HolderType(self._left._innerHolders[name], self._right._innerHolders['blank']) for name in self._left.symbolList
            }
        elif len(self._left.symbolList) == 0:
            self._innerHolders = {
                name: HolderType(self._left._innerHolders['blank'], self._right._innerHolders[name]) for name in self._right.symbolList
            }
        else:
            self._innerHolders = {
                name: HolderType(self._left._innerHolders[name], self._right._innerHolders[name]) for name in self._left.symbolList
            }

    @property
    def dependency(self):
        left = self._left.dependency
        right = self._right.dependency
        return _merge2dict(left, right)

    @property
    def value(self):
        res = {}
        for name in self._innerHolders:
            try:
                res[name] = self._innerHolders[name].value
            except:
                res[name] = np.nan
        return SecuritiesValues(res)


class SecurityAddedValueHolder(SecurityCombinedValueHolder):

    def __init__(self, left, right):
        super(SecurityAddedValueHolder, self).__init__(left, right, AddedValueHolder)


class SecuritySubbedValueHolder(SecurityCombinedValueHolder):

    def __init__(self, left, right):
        super(SecuritySubbedValueHolder, self).__init__(left, right, MinusedValueHolder)


class SecurityMultipliedValueHolder(SecurityCombinedValueHolder):

    def __init__(self, left, right):
        super(SecurityMultipliedValueHolder, self).__init__(left, right, MultipliedValueHolder)


class SecurityDividedValueHolder(SecurityCombinedValueHolder):

    def __init__(self, left, right):
        super(SecurityDividedValueHolder, self).__init__(left, right, DividedValueHolder)


def SecurityShiftedValueHolder(secValueHolder, n):
    assert n >= 1, "shift value should always not be less than 1"
    res = copy.deepcopy(secValueHolder)
    res._window = secValueHolder.window + n
    res._innerHolders = {
        name: Shift(secValueHolder._innerHolders[name], n) for name in secValueHolder._innerHolders
    }
    return res


class SecurityCompoundedValueHolder(SecurityValueHolder):

    def __init__(self, left, right):
        self._returnSize =right.valueSize
        self._symbolList = left.symbolList
        self._window = left.window + right.window - 1
        self._pNames = left._pNames
        if not isinstance(right._pNames, str):
            assert left.valueSize == len(right._pNames)
        else:
            assert left.valueSize == 1

        self._right = copy.deepcopy(right._innerHolders[right._innerHolders.keys()[0]])
        self._isNamed = False
        self._left = copy.deepcopy(left._innerHolders[left._innerHolders.keys()[0]])
        self._innerHolders = {
            name: CompoundedValueHolder(self._left, self._right) for name in self._symbolList
        }

    def push(self, data):
        names = set(self._symbolList).intersection(set(data.keys()))
        for name in names:
            self._innerHolders[name].push(**data[name])

    @property
    def value(self):
        res = {}
        for name in self._innerHolders:
            try:
                res[name] = self._innerHolders[name].value
            except:
                res[name] = np.nan
        return SecuritiesValues(res)


def dependencyCalculator(*args):
    res = defaultdict(list)
    tmp = {}
    for value in args:
        tmp = _merge2dict(tmp, value.dependency)

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