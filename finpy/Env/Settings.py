# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

from finpy.DateUtilities import Date

class MetaSettings(type):

    _evaluationDate = Date.todaysDate()

    def _getEvaluationDate(self):
        return self._evaluationDate

    def _setEvaluationDate(self, value):

        assert isinstance(value, Date), "invalid date for {0}".format(value)
        self._evaluationDate = value

    evaluationDate = property(_getEvaluationDate, _setEvaluationDate)

class Settings(object):
    __metaclass__ = MetaSettings

