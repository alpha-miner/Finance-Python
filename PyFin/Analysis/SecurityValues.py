# -*- coding: utf-8 -*-
u"""
Created on 2017-1-17

@author: cheng.li
"""

from collections import OrderedDict
import numpy as np


class SecurityValues:
    def __init__(self, data, index=None):
        if isinstance(data, dict):
            index = data.keys()
            data = np.array(list(data.values()))

        if isinstance(data, np.ndarray):
            self.values = data
        else:
            self.values = np.array(data)

        if isinstance(index, OrderedDict):
            self.name_mapping = index
        else:
            self.name_mapping = OrderedDict(zip(index, range(len(index))))

        self.name_array = None

    def __getitem__(self, name):
        if not isinstance(name, list):
            return self.values[self.name_mapping[name]]
        else:
            data = np.array([self.values[self.name_mapping[n]] for n in name])
            return SecurityValues(data, name)

    def mask(self, flags):
        if not self.name_array:
            self.name_array = np.array(list(self.name_mapping.keys()))
        return SecurityValues(self.values[flags], self.name_array[flags])

    def __neg__(self):
        return SecurityValues(-self.values, self.name_mapping)

    def __add__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values + right.values, self.name_mapping)
        else:
            return SecurityValues(self.values + right, self.name_mapping)

    def __radd__(self, left):
        if isinstance(left, SecurityValues):
            return SecurityValues(left.values + self.values, self.name_mapping)
        else:
            return SecurityValues(left + self.values, self.name_mapping)

    def __sub__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values - right.values, self.name_mapping)
        else:
            return SecurityValues(self.values - right, self.name_mapping)

    def __rsub__(self, left):
        if isinstance(left, SecurityValues):
            return SecurityValues(left.values - self.values, self.name_mapping)
        else:
            return SecurityValues(left - self.values, self.name_mapping)

    def __mul__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values * right.values, self.name_mapping)
        else:
            return SecurityValues(self.values * right, self.name_mapping)

    def __rmul__(self, left):
        if isinstance(left, SecurityValues):
            return SecurityValues(left.values * self.values, self.name_mapping)
        else:
            return SecurityValues(left * self.values, self.name_mapping)

    def __truediv__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values / right.values, self.name_mapping)
        else:
            return SecurityValues(self.values / right, self.name_mapping)

    def __rtruediv__(self, left):
        if isinstance(left, SecurityValues):
            return SecurityValues(left.values / self.values, self.name_mapping)
        else:
            return SecurityValues(left / self.values, self.name_mapping)

    def __div__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values / right.values, self.name_mapping)
        else:
            return SecurityValues(self.values / right, self.name_mapping)

    def __rdiv__(self, left):
        if isinstance(left, SecurityValues):
            return SecurityValues(left.values / self.values, self.name_mapping)
        else:
            return SecurityValues(left / self.values, self.name_mapping)

    def __and__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values & right.values, self.name_mapping)
        else:
            return SecurityValues(self.values & right, self.name_mapping)

    def __rand__(self, left):
        if isinstance(left, SecurityValues):
            return SecurityValues(left.values & self.values, self.name_mapping)
        else:
            return SecurityValues(left & self.values, self.name_mapping)

    def __or__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values | right.values, self.name_mapping)
        else:
            return SecurityValues(self.values | right, self.name_mapping)

    def __ror__(self, left):
        if isinstance(left, SecurityValues):
            return SecurityValues(left.values | self.values, self.name_mapping)
        else:
            return SecurityValues(left | self.values, self.name_mapping)

    def __eq__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values == right.values, self.name_mapping)
        else:
            return SecurityValues(self.values == right, self.name_mapping)

    def __ne__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values != right.values, self.name_mapping)
        else:
            return SecurityValues(self.values != right, self.name_mapping)

    def __le__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values <= right.values, self.name_mapping)
        else:
            return SecurityValues(self.values <= right, self.name_mapping)

    def __lt__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values < right.values, self.name_mapping)
        else:
            return SecurityValues(self.values < right, self.name_mapping)

    def __ge__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values >= right.values, self.name_mapping)
        else:
            return SecurityValues(self.values >= right, self.name_mapping)

    def __gt__(self, right):
        if isinstance(right, SecurityValues):
            return SecurityValues(self.values > right.values, self.name_mapping)
        else:
            return SecurityValues(self.values > right, self.name_mapping)

    @property
    def index(self):
        return self.name_mapping.keys()

    def __contains__(self, key):
        return key in self.name_mapping

    def __len__(self):
        return self.values.__len__()

    def rank(self):
        return SecurityValues(self.values.argsort().argsort() + 1., self.name_mapping)

    def mean(self):
        return self.values.mean()

    def dot(self, right):
        return np.dot(self.values, right.values)
