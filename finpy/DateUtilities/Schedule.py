# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

from finpy.Enums import BizDayConventions
from finpy.Enums import DateGeneration
from finpy.DateUtilities import Period

class Schedule(object):

    def __init__(self,
                 effectiveDate,
                 terminationDate,
                 tenor,
                 calendar,
                 convention = BizDayConventions.Following,
                 terminationConvention = BizDayConventions.Following,
                 dateGenerationRule = DateGeneration.Forward,
                 endOfMonth = False,
                 firstDate = None,
                 nextToLastDate = None):

        # Initialize priavte data
        self._tenor = tenor
        self._cal = calendar
        self._convention = convention
        self._terminationConvention = terminationConvention
        if tenor < Period("1M"):
            self._endOfMonth = False
        else:
            self._endOfMonth = endOfMonth

        if firstDate == effectiveDate:
            self._firstDate = None
        else:
            self._firstDate = firstDate

        if nextToLastDate == terminationDate:
            self._nextToLastDate = None
        else:
            self._nextToLastDate = nextToLastDate

        # in many cases (e.g. non-expired bonds) the effective date is not
        # really necessary. In these cases a decent placeholder is enough
        if effectiveDate is None and firstDate is None and dateGenerationRule == DateGeneration.Backward:
            pass

