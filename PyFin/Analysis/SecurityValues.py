# -*- coding: utf-8 -*-
u"""
Created on 2017-1-17

@author: cheng.li
"""

import numpy as np


class SecurityValues:
    def __init__(self, data, index):
        if isinstance(data, np.ndarray):
            self.values = data
        else:
            self.values = np.array(data)

        if isinstance(index, dict):
            self.name_mapping = index
        else:
            self.name_mapping = dict(zip(index, range(len(index))))

    def __getitem__(self, name):
        return self.values[self.name_mapping[name]]

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

    @property
    def index(self):
        return self.name_mapping.keys()