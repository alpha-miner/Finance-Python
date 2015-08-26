# -*- coding: utf-8 -*-
u"""
Created on 2015-8-14

@author: cheng.li
"""

from PyFin.DateUtilities import Date
from PyFin.Patterns.Singleton import Singleton
from PyFin.Utilities import pyFinAssert


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
            raise ValueError("{0} is not a valid PyFin date object".format(value))
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
        pyFinAssert(len(value) != 0, ValueError, "default symbol list can't be set to empty")
        self._defaultSymbolList = [v.lower() for v in value]


Settings = SettingsFactory()
