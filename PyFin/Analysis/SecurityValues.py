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
            index = OrderedDict(zip(data.keys(), range(len(data))))
            data = np.array(list(data.values()))

        self.values = data
        self.name_mapping = index
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

        filtered_names = self.name_array[flags]
        return SecurityValues(self.values[flags], OrderedDict(zip(filtered_names, range(len(filtered_names)))))

    def __invert__(self):
        return SecurityValues(~self.values, self.name_mapping)

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
        data = self.values.argsort().argsort().astype(float)
        data[np.isnan(self.values)] = np.nan
        return SecurityValues(data + 1., self.name_mapping)

    def mean(self):
        return np.nanmean(self.values)

    def dot(self, right):
        return np.dot(self.values, right.values)
