# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

import copy
import numpy as np
from PyFin.Analysis.SecurityValues import SecurityValues
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder


class CrossSectionValueHolder(SecurityValueHolder):

    def __init__(self, innerValue):
        if isinstance(innerValue, SecurityValueHolder):
            self._inner = copy.deepcopy(innerValue)
        elif isinstance(innerValue, str):
            self._inner = SecurityLatestValueHolder(innerValue)
        else:
            raise ValueError("Currently only value holder input is allowed for rank holder.")
        self._window = self._inner.window
        self._returnSize = self._inner.valueSize
        self._dependency = copy.deepcopy(self._inner._dependency)
        self.updated = False
        self.cached = None

    @property
    def symbolList(self):
        return self._inner.symbolList

    @property
    def holders(self):
        return self._inner.holders

    def push(self, data):
        self._inner.push(data)
        self.updated = False


class CSRankedSecurityValueHolder(CrossSectionValueHolder):

    def __init__(self, innerValue):
        super(CSRankedSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            self.cached = raw_values.rank()
            self.updated = True
            return self.cached

    def value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            self.cached = raw_values.rank()
            self.updated = True
            return self.cached[name]

    def value_by_names(self, names):
        raw_values = self._inner.value_by_names(names)
        raw_values = raw_values.rank()
        return raw_values

    def __deepcopy__(self, memo):
        return CSRankedSecurityValueHolder(self._inner)


class CSAverageSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue):
        super(CSAverageSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            mean_value = np.array([raw_values.mean()] * len(raw_values))
            mean_value[np.isnan(raw_values.values)] = np.nan
            self.cached = SecurityValues(mean_value, raw_values.name_mapping)
            self.updated = True
            return self.cached

    def value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            mean_value = np.array([raw_values.mean()] * len(raw_values))
            mean_value[np.isnan(raw_values.values)] = np.nan
            self.cached = SecurityValues(mean_value, raw_values.name_mapping)
            self.updated = True
            return self.cached[name]

    def value_by_names(self, names):
        raw_values = self._inner.value_by_names(names)
        mean_value = np.array([raw_values.mean()] * len(raw_values))
        mean_value[np.isnan(raw_values.values)] = np.nan
        raw_values = SecurityValues(mean_value, raw_values.name_mapping)
        return raw_values[names]

    def __deepcopy__(self, memo):
        return CSRankedSecurityValueHolder(self._inner)


class CSAverageAdjustedSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue):
        super(CSAverageAdjustedSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            self.cached = raw_values - raw_values.mean()
            self.updated = True
            return self.cached

    def value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            self.cached = raw_values - raw_values.mean()
            self.updated = True
            return self.cached[name]

    def value_by_names(self, names):
        raw_values = self._inner.value_by_names(names)
        raw_values = raw_values - raw_values.mean()
        return raw_values[names]

    def __deepcopy__(self, memo):
        return CSRankedSecurityValueHolder(self._inner)


class CSQuantileSecurityValueHolder(CrossSectionValueHolder):
    def __init__(self, innerValue):
        super(CSQuantileSecurityValueHolder, self).__init__(innerValue)

    @property
    def value(self):
        if self.updated:
            return self.cached
        else:
            raw_values = self._inner.value
            self.cached = (raw_values.rank() - 1.) / (len(raw_values) - 1.)
            self.updated = True
            return self.cached

    def value_by_name(self, name):
        if self.updated:
            return self.cached[name]
        else:
            raw_values = self._inner.value
            self.cached = (raw_values.rank() - 1.) / (len(raw_values) - 1.)
            self.updated = True
            return self.cached[name]

    def value_by_names(self, names):
        raw_values = self._inner.value_by_names(names)
        raw_values = (raw_values.rank() - 1.) / (len(raw_values) - 1.)
        return raw_values[names]

    def __deepcopy__(self, memo):
        return CSRankedSecurityValueHolder(self._inner)
