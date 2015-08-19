# -*- coding: utf-8 -*-
u"""
Created on 2015-7-21

@author: cheng.li
"""

from collections import OrderedDict
from PyFin.Utilities import pyFinAssert


class Timeseries(object):
    def __init__(self, dates, values):
        pyFinAssert(len(dates) == len(values), ValueError, "dates and values should have same length")
        self._values = OrderedDict()

        for date, value in zip(dates, values):
            self._values[date] = value

    def firstDate(self):
        return list(self._values.keys())[0]

    def lastDate(self):
        return list(self._values.keys())[-1]

    def size(self):
        return len(self._values)

    def __getitem__(self, date):
        return self._values[date]
