# -*- coding: utf-8 -*-
u"""
Created on 2015-7-21

@author: cheng.li
"""

from PyFin.Enums.NormalizingType import NormalizingType
from PyFin.DateUtilities.Calendar import Calendar


class Normalizer(object):
    def __init__(self, type=NormalizingType.Null):
        self._previous = None
        self._current = None
        self._type = type

        if self._type == NormalizingType.BizDay or self._type == NormalizingType.CalendarDay:
            self._isFirst = True
            if self._type == NormalizingType.BizDay:
                self._cal = Calendar('China.SSE')

    def normalizeOneDayReturn(self, pDate, pReturn):
        if self._type == NormalizingType.Null:
            return pReturn
        elif self._type == NormalizingType.CalendarDay:
            return self._calendarDayCalcualtion(pDate, pReturn)
        elif self._type == NormalizingType.BizDay:
            return self._bizDayCalculation(pDate, pReturn)

    def _calendarDayCalcualtion(self, pDate, pReturn):
        if self._isFirst:
            self._isFirst = False
        else:
            daysBetween = pDate - self._previous
            pReturn /= daysBetween

        self._previous = pDate
        return pReturn

    def _bizDayCalculation(self, pDate, pReturn):
        if self._isFirst:
            self._isFirst = False
        else:
            daysBetween = self._cal.bizDaysBetween(self._previous, pDate, True, False)
            pReturn /= daysBetween

        self._previous = pDate
        return pReturn
