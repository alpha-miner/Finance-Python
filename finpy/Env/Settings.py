# -*- coding: utf-8 -*-
u"""
Created on 2015-8-14

@author: cheng.li
"""

from finpy.DateUtilities import Date
from finpy.Patterns.Singleton import Singleton


class SettingsFactory(Singleton):
    def __init__(self, forcedBuild=False):
        self._evaluationDate = None

    @property
    def evaluationDate(self):
        if self._evaluationDate is None:
            return Date.todaysDate()
        return self._evaluationDate

    @evaluationDate.setter
    def evaluationDate(self, value):
        if not isinstance(value, Date):
            raise ValueError("{0} is not a valid finpy date object".format(value))
        self._evaluationDate = value

    def resetEvaluationDate(self):
        self._evaluationDate = None

    def anchorEvaluationDate(self):
        if self._evaluationDate is None:
            self._evaluationDate = Date.todaysDate()


Settings = SettingsFactory()
