# -*- coding: utf-8 -*-
u"""
Created on 2015-8-14

@author: cheng.li
"""

from fp.DateUtilities import Date
from fp.Patterns.Singleton import Singleton
from fp.Utilities import fpAssert


class SettingsFactory(Singleton):
    def __init__(self, forcedBuild=False):
        self._evaluationDate = None
        self._defaultSymbolList = set(['600000.xshg'])

    @property
    def evaluationDate(self):
        if self._evaluationDate is None:
            return Date.todaysDate()
        return self._evaluationDate

    @evaluationDate.setter
    def evaluationDate(self, value):
        if not isinstance(value, Date):
            raise ValueError("{0} is not a valid fp date object".format(value))
        self._evaluationDate = value

    def resetEvaluationDate(self):
        self._evaluationDate = None

    def anchorEvaluationDate(self):
        if self._evaluationDate is None:
            self._evaluationDate = Date.todaysDate()

    @property
    def defaultSymbolList(self):
        return self._defaultSymbolList

    @defaultSymbolList.setter
    def defaultSymbolList(self, value):
        fpAssert(len(value) != 0, ValueError, "default symbol list can't be set to empty")
        self._defaultSymbolList = value


Settings = SettingsFactory()
