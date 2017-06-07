# -*- coding: utf-8 -*-
u"""
Created on 2015-8-14

@author: cheng.li
"""

from PyFin.DateUtilities import Date
from PyFin.Utilities import pyFinAssert


class SettingsFactory(object):
    def __init__(self):
        self._evaluationDate = None
        self._includeToday = None

    @property
    def evaluationDate(self):
        if not self._evaluationDate:
            return Date.todaysDate()
        return self._evaluationDate

    @evaluationDate.setter
    def evaluationDate(self, value):
        pyFinAssert(isinstance(value, Date), ValueError, "{0} is not a valid PyFin date object".format(value))
        self._evaluationDate = value

    @property
    def includeTodaysCashFlows(self):
        return self._includeToday

    @includeTodaysCashFlows.setter
    def includeTodaysCashFlows(self, value):
        self._evaluationDate = value

    def resetEvaluationDate(self):
        self._evaluationDate = None

    def anchorEvaluationDate(self):
        if self._evaluationDate is None:
            self._evaluationDate = Date.todaysDate()


Settings = SettingsFactory()
