# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

from PyFin.Enums import BizDayConventions
from PyFin.Enums import DateGeneration
from PyFin.Enums import TimeUnits
from PyFin.DateUtilities import Date
from PyFin.DateUtilities import Period
from PyFin.DateUtilities import Calendar
from PyFin.Env import Settings
from PyFin.Utilities import pyFinAssert


class Schedule(object):
    def __init__(self,
                 effectiveDate,
                 terminationDate,
                 tenor,
                 calendar,
                 convention=BizDayConventions.Following,
                 terminationConvention=BizDayConventions.Following,
                 dateGenerationRule=DateGeneration.Forward,
                 endOfMonth=False,
                 firstDate=None,
                 nextToLastDate=None):

        # Initialize private data
        self._tenor = tenor
        self._cal = calendar
        self._convention = convention
        self._terminationConvention = terminationConvention
        self._rule = dateGenerationRule
        self._dates = []
        self._isRegular = []

        if tenor < Period("1M"):
            self._endOfMonth = False
        else:
            self._endOfMonth = endOfMonth

        if firstDate is None or firstDate == effectiveDate:
            self._firstDate = None
        else:
            self._firstDate = firstDate

        if nextToLastDate is None or nextToLastDate == terminationDate:
            self._nextToLastDate = None
        else:
            self._nextToLastDate = nextToLastDate

        # in many cases (e.g. non-expired bonds) the effective date is not
        # really necessary. In these cases a decent placeholder is enough
        if effectiveDate is None and firstDate is None and dateGenerationRule == DateGeneration.Backward:
            evalDate = Settings.evaluationDate
            pyFinAssert(evalDate < terminationDate, ValueError, "null effective date")
            if nextToLastDate is not None:
                y = int((nextToLastDate - evalDate) / 366) + 1
                effectiveDate = nextToLastDate - Period(y, TimeUnits.Years)
            else:
                y = int((terminationDate - evalDate) / 366) + 1
                effectiveDate = terminationDate - Period(y, TimeUnits.Years)
        else:
            pyFinAssert(effectiveDate is not None, ValueError, "null effective date")

        pyFinAssert(effectiveDate < terminationDate, ValueError, "effective date ({0}) "
                                                              "later than or equal to termination date ({1}"
                 .format(effectiveDate, terminationDate))

        if tenor.length == 0:
            self._rule = DateGeneration.Zero
        else:
            pyFinAssert(tenor.length > 0, ValueError, "non positive tenor ({0:d}) not allowed".format(tenor.length))

        if self._firstDate is not None:
            if self._rule == DateGeneration.Backward or self._rule == DateGeneration.Forward:
                pyFinAssert(effectiveDate < self._firstDate < terminationDate, ValueError,
                         "first date ({0}) out of effective-termination date range [{1}, {2})"
                         .format(self._firstDate, effectiveDate, terminationDate))
                # we should ensure that the above condition is still
                # verified after adjustment
            elif self._rule == DateGeneration.Zero:
                raise ValueError("first date incompatible with {0:d} date generation rule".format(self._rule))
            else:
                raise ValueError("unknown rule ({0:d})".format(self._rule))

        if self._nextToLastDate is not None:
            if self._rule == DateGeneration.Backward or self._rule == DateGeneration.Forward:
                pyFinAssert(effectiveDate < self._nextToLastDate < terminationDate, ValueError,
                         "next to last date ({0}) out of effective-termination date range [{1}, {2})"
                         .format(self._nextToLastDate, effectiveDate, terminationDate))
                # we should ensure that the above condition is still
                # verified after adjustment
            elif self._rule == DateGeneration.Zero:
                raise ValueError("next to last date incompatible with {0:d} date generation rule".format(self._rule))
            else:
                raise ValueError("unknown rule ({0:d})".format(self._rule))

        # calendar needed for endOfMonth adjustment
        nullCalendar = Calendar("Null")
        periods = 1

        if self._rule == DateGeneration.Zero:
            self._tenor = Period(0, TimeUnits.Years)
            self._dates.extend([effectiveDate, terminationDate])
            self._isRegular.append(True)
        elif self._rule == DateGeneration.Backward:
            self._dates.append(terminationDate)
            seed = terminationDate
            if self._nextToLastDate is not None:
                self._dates.insert(0, self._nextToLastDate)
                temp = nullCalendar.advanceDate(seed, Period(-periods * self._tenor.length, self._tenor.units),
                                                convention, self._endOfMonth)
                if temp != self._nextToLastDate:
                    self._isRegular.insert(0, False)
                else:
                    self._isRegular.insert(0, True)
                seed = self._nextToLastDate

            exitDate = effectiveDate
            if self._firstDate is not None:
                exitDate = self._firstDate

            while True:
                temp = nullCalendar.advanceDate(seed, Period(-periods * self._tenor.length, self._tenor.units),
                                                convention, self._endOfMonth)
                if temp < exitDate:
                    if self._firstDate is not None and self._cal.adjustDate(self._dates[0],
                                                                            convention) != self._cal.adjustDate(
                            self._firstDate, convention):
                        self._dates.insert(0, self._firstDate)
                        self._isRegular.insert(0, False)
                    break
                else:
                    # skip dates that would result in duplicates
                    # after adjustment
                    if self._cal.adjustDate(self._dates[0], convention) != self._cal.adjustDate(temp, convention):
                        self._dates.insert(0, temp)
                        self._isRegular.insert(0, True)
                    periods += 1

            if self._cal.adjustDate(self._dates[0], convention) != self._cal.adjustDate(effectiveDate, convention):
                self._dates.insert(0, effectiveDate)
                self._isRegular.insert(0, False)

        elif self._rule == DateGeneration.Forward:
            self._dates.append(effectiveDate)

            seed = self._dates[-1]

            if self._firstDate is not None:
                self._dates.append(self._firstDate)
                temp = nullCalendar.advanceDate(seed, Period(periods * self._tenor.length, self._tenor.units),
                                                convention, self._endOfMonth)
                if temp != self._firstDate:
                    self._isRegular.append(False)
                else:
                    self._isRegular.append(True)
                seed = self._firstDate

            exitDate = terminationDate
            if self._nextToLastDate is not None:
                exitDate = self._nextToLastDate

            while True:
                temp = nullCalendar.advanceDate(seed, Period(periods * self._tenor.length, self._tenor.units),
                                                convention, self._endOfMonth)
                if temp > exitDate:
                    if self._nextToLastDate is not None and self._cal.adjustDate(self._dates[-1],
                                                                                 convention) != self._cal.adjustDate(
                            self._nextToLastDate, convention):
                        self._dates.append(self._nextToLastDate)
                        self._isRegular.append(False)
                    break
                else:
                    # skip dates that would result in duplicates
                    # after adjustment
                    if self._cal.adjustDate(self._dates[-1], convention) != self._cal.adjustDate(temp, convention):
                        self._dates.append(temp)
                        self._isRegular.append(True)
                    periods += 1

            if self._cal.adjustDate(self._dates[-1], terminationConvention) != self._cal.adjustDate(terminationDate,
                                                                                                    terminationConvention):
                self._dates.append(terminationDate)
                self._isRegular.append(False)
        else:
            raise ValueError("unknown rule ({0:d})".format(self._rule))

        # adjustments
        if self._endOfMonth and self._cal.isEndOfMonth(seed):
            # adjust to end of month
            if convention == BizDayConventions.Unadjusted:
                for i in range(len(self._dates) - 1):
                    self._dates[i] = Date.endOfMonth(self._dates[i])
            else:
                for i in range(len(self._dates) - 1):
                    self._dates[i] = self._cal.endOfMonth(self._dates[i])

            if terminationConvention != BizDayConventions.Unadjusted:
                self._dates[0] = self._cal.endOfMonth(self._dates[0])
                self._dates[-1] = self._cal.endOfMonth(self._dates[-1])
            else:
                if self._rule == DateGeneration.Backward:
                    self._dates[-1] = Date.endOfMonth(self._dates[-1])
                else:
                    self._dates[0] = Date.endOfMonth(self._dates[0])
        else:
            for i in range(len(self._dates) - 1):
                self._dates[i] = self._cal.adjustDate(self._dates[i], convention)

            if terminationConvention != BizDayConventions.Unadjusted:
                self._dates[-1] = self._cal.adjustDate(self._dates[-1], terminationConvention)

        # Final safety checks to remove extra next-to-last date, if
        # necessary.  It can happen to be equal or later than the end
        # date due to EOM adjustments (see the Schedule test suite
        # for an example).

        if len(self._dates) >= 2 and self._dates[len(self._dates) - 2] >= self._dates[-1]:
            self._isRegular[len(self._dates) - 2] = (self._dates[len(self._dates) - 2] == self._dates[-1])
            self._dates[len(self._dates) - 2] = self._dates[-1]
            self._dates.pop()
            self._isRegular.pop()

        if len(self._dates) >= 2 and self._dates[1] <= self._dates[0]:
            self._isRegular[1] = (self._dates[1] == self._dates[0])
            self._dates[1] = self._dates[0]
            self._dates = self._dates[1:]
            self._isRegular = self._isRegular[1:]

        pyFinAssert(len(self._dates) >= 1, ValueError, "degenerate single date ({0}) schedule\n"
                                                    "seed date: {1}\n"
                                                    "exit date: {2}\n"
                                                    "effective date: {3}\n"
                                                    "first date: {4}\n"
                                                    "next to last date: {5}\n"
                                                    "termination date: {6}\n"
                                                    "generation rule: {7}\n"
                                                    "end of month: {8}\n"
                 .format(self._dates[0],
                         seed, exitDate,
                         effectiveDate,
                         firstDate,
                         nextToLastDate,
                         terminationDate,
                         self._rule, self._endOfMonth))

    def size(self):
        return len(self._dates)

    def __getitem__(self, item):
        return self._dates[item]
