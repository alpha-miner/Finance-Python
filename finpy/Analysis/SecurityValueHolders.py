# -*- coding: utf-8 -*-
u"""
Created on 2015-8-7

@author: cheng.li
"""

from abc import ABCMeta
import copy
import numpy as np
from finpy.Math.Accumulators.StatefulAccumulators import MovingAverage


class SecuritiesValues(object):

    def __init__(self, values):
        self._values = values

    def __getitem__(self, item):
        return self._values[item]

    def __neg__(self):
        return SecuritiesValues({
            name: -self._values[name] for name in self._values
        })

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
        if isinstance(left, SecuritiesValues):
            assert self._values.keys() == left._values.keys(), "left security names {0} is not equal to right {1}" \
                                                                .format(left._values.keys(), self._values.keys())
            return SecuritiesValues(
                {
                    name: left._values[name] - self._values[name] for name in self._values
                }
            )
        else:
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
        if isinstance(left, SecuritiesValues):
            assert self._values.keys() == left._values.keys(), "left security names {0} is not equal to right {1}" \
                                                               .format(left._values.keys(), self._values.keys())
            return SecuritiesValues(
                {
                    name: left._values[name] / self._values[name] for name in self._values
                }
            )
        else:
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


class NamedValueHolder(object):
    def __init__(self, symbol, valueHolder):
        self._valueHolder = copy.deepcopy(valueHolder)
        self._symbolList = [symbol]

    def push(self, data):
        name = set(self._symbolList).intersection(set(data.keys()))
        if name:
            self._valueHolder.push(**data[name.pop()])

    @property
    def value(self):
        try:
            return self._valueHolder.value
        except:
            return np.nan

    @property
    def dependency(self):
        return self._valueHolder._pNames

    @property
    def window(self):
        return 1

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


class SecurityValueHolder(object):

    __metaclass__ = ABCMeta

    def __init__(self, pNames='x', symbolList=None):
        if symbolList is None:
            # should do something to get a global value here
            self._symbolList = set(['600000.XSHG', 'AAPL', 'GOOG', "Lenovo"])
        else:
            self._symbolList = set(symbolList)
        self._pNames = pNames

    @property
    def symbolList(self):
        return self._symbolList

    @property
    def dependency(self):
        return self._pNames

    @property
    def window(self):
        return 1

    def push(self, data):
        names = self._symbolList.intersection(set(data.keys()))
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
            res._symbolList = set(item)
            assert len(res._symbolList) == len(item), "security name can't be duplicated"
            res._innerHolders = \
                {
                    name: self._innerHolders[name] for name in res._symbolList
                }
            return res
        elif item in self._innerHolders:
            return NamedValueHolder(item, self._innerHolders[item])
        else:
            raise TypeError("")

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

    def __init__(self, value):
        self._value = value
        self._symbolList = []

    def push(self, data):
        pass

    @property
    def value(self):
        return self._value


class SecurityCombinedValueHolder(SecurityValueHolder):

    def __init__(self, left, right):
        if isinstance(left, SecurityValueHolder) or isinstance(left, NamedValueHolder):
            self._left = copy.deepcopy(left)
            self._right = copy.deepcopy(right)
            if isinstance(right, NamedValueHolder) or isinstance(right, SecurityValueHolder):
                self._symbolList = set(self._left._symbolList).union(set(right._symbolList))
            else:
                self._symbolList = set(self._left._symbolList)
        else:
            self._left = IdentitySecurityValueHolder(left)
            self._right = copy.deepcopy(right)
            if isinstance(right, NamedValueHolder) or isinstance(right, SecurityValueHolder):
                self._symbolList = set(self._left._symbolList).union(set(right._symbolList))
            else:
                self._symbolList = set(self._left._symbolList)

    def push(self, data):
        self._left.push(data)
        if isinstance(self._right, NamedValueHolder) or isinstance(self._right, SecurityValueHolder):
            self._right.push(data)

    @property
    def left(self):
        return self._left.value

    @property
    def right(self):
        if isinstance(self._right, NamedValueHolder) or isinstance(self._right, SecurityValueHolder):
            return self._right.value
        else:
            return self._right


class SecurityAddedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityAddedValueHolder, self).__init__(left, right)

    @property
    def value(self):
        return self.left + self.right


class SecuritySubbedValueHolder(SecurityCombinedValueHolder):

    def __init__(self, left, right):
        super(SecuritySubbedValueHolder, self).__init__(left, right)

    @property
    def value(self):
        return self.left - self.right


class SecurityMultipliedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityMultipliedValueHolder, self).__init__(left, right)

    @property
    def value(self):
        return self.left * self.right


class SecurityDividedValueHolder(SecurityCombinedValueHolder):
    def __init__(self, left, right):
        super(SecurityDividedValueHolder, self).__init__(left, right)

    @property
    def value(self):
        return self.left / self.right


class SecurityMovingAverage(SecurityValueHolder):

    def __init__(self, window, pNames='x', symbolList=None):
        super(SecurityMovingAverage, self).__init__(pNames, symbolList)
        self._window = window
        self._innerHolders = \
            {
                name: MovingAverage(self._window, self._pNames) for name in self._symbolList
            }


if __name__ == "__main__":
    # inializing the value holde
    symbolList = ['600000.XSHG', 'AAPL', 'GOOG', "Lenovo"]
    ma = SecurityMovingAverage(20, 'close')
    ma2 = SecurityMovingAverage(10, 'open')
    ma3 = ma['AAPL'] / ma - 3.0

    # prepare the data
    data = {'600000.XSHG': {'close': 6.0, 'open': 15.0},
            'AAPL': {'close': 12.0, 'open': 10.0},
            'GOOG': {'close': 24.0, 'open': 17.0}}

    data2 = {str(i): {'close': 3.0} for i in range(30)}
    data.update(data2)

    # push and pop
    for i in range(100):
        ma3.push(data)
        print(ma3.value)