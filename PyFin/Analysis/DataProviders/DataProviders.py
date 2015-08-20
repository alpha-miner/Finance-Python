# -*- coding: utf-8 -*-
u"""
Created on 2015-8-19

@author: cheng.li
"""

import copy


class DataProvider(object):
    def __init__(self):
        self._data = {}

    def set(self, symbol, field, value):
        symbol = symbol.lower()
        field = field.lower()
        if symbol not in self._data:
            self._data[symbol] = {}
        if field in self._data[symbol]:
            raise ValueError("symbol {0}'s field ({1}) can't be assigned again".format(symbol, field))
        self._data[symbol][field] = value

    @property
    def data(self):
        return copy.deepcopy(self._data)

    def clear(self):
        self._data = {}
