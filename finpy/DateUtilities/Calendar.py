# -*- coding: utf-8 -*-
u"""
Created on 2015-7-9

@author: cheng.li
"""

from finpy.Enums.Weekdays import Weekdays
from finpy.Enums.Months import Months
from finpy.Enums.BizDayConventions import BizDayConventions
from finpy.Enums.TimeUnits import TimeUnits
from finpy.DateUtilities.Date import Date
from finpy.DateUtilities.Period import Period


class Calendar(object):
    def __init__(self, holCenter):
        holCenter = holCenter.lower()
        self._impl = _holDict[holCenter]()

    def isBizDay(self, d):
        return self._impl.isBizDay(d)

    def isHoliday(self, d):
        return not self.isBizDay(d)

    def isWeekEnd(self, weekday):
        return self._impl.isWeekEnd(weekday)

    def isEndOfMonth(self, d):
        return d.month() != self.adjustDate(d+1).month()

    def endOfMonth(self, d):
        return self.adjustDate(Date.endOfMonth(d), BizDayConventions.Preceding)

    def adjustDate(self, d, c = BizDayConventions.Following):
        if c == BizDayConventions.Unadjusted:
            return d

        d1 = d

        if c == BizDayConventions.Following or c == BizDayConventions.ModifiedFollowing or \
                c == BizDayConventions.HalfMonthModifiedFollowing:
            while self.isHoliday(d1):
                d1 += 1
            if c == BizDayConventions.ModifiedFollowing or c == BizDayConventions.HalfMonthModifiedFollowing:
                if d1.month() != d.month():
                    return self.adjustDate(d, BizDayConventions.Preceding)
                if c == BizDayConventions.HalfMonthModifiedFollowing:
                    if d.dayOfMonth() <= 15 and d1.dayOfMonth() > 15:
                        return self.adjustDate(d, BizDayConventions.Preceding)
        elif c == BizDayConventions.Preceding or c == BizDayConventions.ModifiedPreceding:
            while self.isHoliday(d1):
                d1 -= 1
            if c == BizDayConventions.ModifiedPreceding and d1.month() != d.month:
                return self.adjustDate(d, BizDayConventions.Following)
        elif c == BizDayConventions.Nearest:
            d2 = d
            while self.isHoliday(d1) and self.isHoliday(d2):
                d1 += 1
                d2 -= 1

            if self.isHoliday(d1):
                return d2
            else:
                return d1
        else:
            raise RuntimeError("unknown business-day convention")
        return d1

    def advanceDate(self, d, period, c = BizDayConventions.Following, endOfMonth = False):

        if isinstance(period, str):
            period = Period(period)

        n = period.length
        units = period.units

        if n == 0:
            return self.adjustDate(d, c)
        elif units == TimeUnits.BDays:
            d1 = d
            if n > 0:
                while n > 0:
                    d1 += 1
                    while self.isHoliday(d1):
                        d1 += 1
                    n -= 1
            else:
                while n < 0:
                    d1 -= 1
                    while self.isHoliday(d1):
                        d1 -= 1
                    n += 1
            return d1
        elif units == TimeUnits.Days or units == TimeUnits.Weeks:
            d1 = d + period
            return self.adjustDate(d1, c)
        else:
            d1 = d + period
            if endOfMonth and self.isEndOfMonth(d):
                return self.endOfMonth(d1)
            return self.adjustDate(d1, c)

    def holDatesList(self, fromDate, toDate, includeWeekEnds = True):
        assert fromDate <= toDate, "from date ({0:s} must be earlier than to date {1:s}".format(fromDate, toDate)
        result = []
        d = fromDate
        while d <= toDate:
            if self.isHoliday(d) and (includeWeekEnds or not self.isWeekEnd(d.weekday())):
                result.append(d)
            d += 1
        return result

    def bizDatesList(self, fromDate, toDate):
        assert fromDate <= toDate, "from date ({0:s} must be earlier than to date {1:s}".format(fromDate, toDate)
        result = []
        d = fromDate
        while d <= toDate:
            if self.isBizDay(d):
                result.append(d)
            d += 1
        return result

class ChinaSseImpl(object):
    def __init__(self):
        pass

    def isBizDay(self, date):
        w = date.weekday()
        d = date.dayOfMonth()
        m = date.month()
        y = date.year()

        if self.isWeekEnd(w) \
                or (d == 1 and m == Months.January) \
                or (y == 2005 and d == 3 and m == Months.January) \
                or (y == 2006 and (d == 2 or d == 3) and m == Months.January) \
                or (y == 2007 and d <= 3 and m == Months.January) \
                or (y == 2007 and d == 31 and m == Months.December) \
                or (y == 2009 and d == 2 and m == Months.January) \
                or (y == 2011 and d == 3 and m == Months.January) \
                or (y == 2012 and (d == 2 or d == 3) and m == Months.January) \
                or (y == 2013 and d <= 3 and m == Months.January) \
                or (y == 2014 and d == 1 and m == Months.January) \
                or (y == 2015 and d <= 3 and m == Months.January) \
                or (y == 2004 and d >= 19 and d <= 28 and m == Months.January) \
                or (y == 2005 and d >= 7 and d <= 15 and m == Months.February) \
                or (y == 2006 and ((d >= 26 and m == Months.January) or (d <= 3 and m == Months.February))) \
                or (y == 2007 and d >= 17 and d <= 25 and m == Months.February) \
                or (y == 2008 and d >= 6 and d <= 12 and m == Months.February) \
                or (y == 2009 and d >= 26 and d <= 30 and m == Months.January) \
                or (y == 2010 and d >= 15 and d <= 19 and m == Months.February) \
                or (y == 2011 and d >= 2 and d <= 8 and m == Months.February) \
                or (y == 2012 and d >= 23 and d <= 28 and m == Months.January) \
                or (y == 2013 and d >= 11 and d <= 15 and m == Months.February) \
                or (y == 2014 and d >= 31 and m == Months.January) \
                or (y == 2014 and d <= 6 and m == Months.February) \
                or (y == 2015 and d >= 18 and d <= 24 and m == Months.February) \
                or (y <= 2008 and d == 4 and m == Months.April) \
                or (y == 2009 and d == 6 and m == Months.April) \
                or (y == 2010 and d == 5 and m == Months.April) \
                or (y == 2011 and d >= 3 and d <= 5 and m == Months.April) \
                or (y == 2012 and d >= 2 and d <= 4 and m == Months.April) \
                or (y == 2013 and d >= 4 and d <= 5 and m == Months.April) \
                or (y == 2014 and d == 7 and m == Months.April) \
                or (y == 2015 and d >= 5 and d <= 6 and m == Months.April) \
                or (y <= 2007 and d >= 1 and d <= 7 and m == Months.May) \
                or (y == 2008 and d >= 1 and d <= 2 and m == Months.May) \
                or (y == 2009 and d == 1 and m == Months.May) \
                or (y == 2010 and d == 3 and m == Months.May) \
                or (y == 2011 and d == 2 and m == Months.May) \
                or (y == 2012 and ((d == 30 and m == Months.April) or (d == 1 and m == Months.May))) \
                or (y == 2013 and ((d >= 29 and m == Months.April) or (d == 1 and m == Months.May))) \
                or (y == 2014 and d >= 1 and d <= 3 and m == Months.May) \
                or (y == 2015 and d == 1 and m == Months.May) \
                or (y <= 2008 and d == 9 and m == Months.June) \
                or (y == 2009 and (d == 28 or d == 29) and m == Months.May) \
                or (y == 2010 and d >= 14 and d <= 16 and m == Months.June) \
                or (y == 2011 and d >= 4 and d <= 6 and m == Months.June) \
                or (y == 2012 and d >= 22 and d <= 24 and m == Months.June) \
                or (y == 2013 and d >= 10 and d <= 12 and m == Months.June) \
                or (y == 2014 and d == 2 and m == Months.June) \
                or (y == 2015 and d == 22 and m == Months.June) \
                or (y <= 2008 and d == 15 and m == Months.September) \
                or (y == 2010 and d >= 22 and d <= 24 and m == Months.September) \
                or (y == 2011 and d >= 10 and d <= 12 and m == Months.September) \
                or (y == 2012 and d == 30 and m == Months.September) \
                or (y == 2013 and d >= 19 and d <= 20 and m == Months.September) \
                or (y == 2014 and d == 8 and m == Months.September) \
                or (y == 2015 and d == 27 and m == Months.September) \
                or (y <= 2007 and d >= 1 and d <= 7 and m == Months.October) \
                or (y == 2008 and ((d >= 29 and m == Months.September) or (d <= 3 and m == Months.October))) \
                or (y == 2009 and d >= 1 and d <= 8 and m == Months.October) \
                or (y == 2010 and d >= 1 and d <= 7 and m == Months.October) \
                or (y == 2011 and d >= 1 and d <= 7 and m == Months.October) \
                or (y == 2012 and d >= 1 and d <= 7 and m == Months.October) \
                or (y == 2013 and d >= 1 and d <= 7 and m == Months.October) \
                or (y == 2014 and d >= 1 and d <= 7 and m == Months.October) \
                or (y == 2015 and d >= 1 and d <= 7 and m == Months.October) \
                or (y == 2015 and d >= 3 and d <= 4 and m == Months.September):
            return False
        return True

    def isHoliday(self, d):
        return not self.isBizDay(d)

    def isWeekEnd(self, weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

class ChinaIBImpl(object):

    _working_weekends = set([
            # 2005
            Date.westernStyle(5, Months.February, 2005),
            Date.westernStyle(6, Months.February, 2005),
            Date.westernStyle(30, Months.April, 2005),
            Date.westernStyle(8, Months.May, 2005),
            Date.westernStyle(8, Months.October, 2005),
            Date.westernStyle(9, Months.October, 2005),
            Date.westernStyle(31, Months.December, 2005),
            #2006
            Date.westernStyle(28, Months.January, 2006),
            Date.westernStyle(29, Months.April, 2006),
            Date.westernStyle(30, Months.April, 2006),
            Date.westernStyle(30, Months.September, 2006),
            Date.westernStyle(30, Months.December, 2006),
            Date.westernStyle(31, Months.December, 2006),
            # 2007
            Date.westernStyle(17, Months.February, 2007),
            Date.westernStyle(25, Months.February, 2007),
            Date.westernStyle(28, Months.April, 2007),
            Date.westernStyle(29, Months.April, 2007),
            Date.westernStyle(29, Months.September, 2007),
            Date.westernStyle(30, Months.September, 2007),
            Date.westernStyle(29, Months.December, 2007),
            # 2008
            Date.westernStyle(2, Months.February, 2008),
            Date.westernStyle(3, Months.February, 2008),
            Date.westernStyle(4, Months.May, 2008),
            Date.westernStyle(27, Months.September, 2008),
            Date.westernStyle(28, Months.September, 2008),
            # 2009
            Date.westernStyle(4, Months.January, 2009),
            Date.westernStyle(24, Months.January, 2009),
            Date.westernStyle(1, Months.February, 2009),
            Date.westernStyle(31, Months.May, 2009),
            Date.westernStyle(27, Months.September, 2009),
            Date.westernStyle(10, Months.October, 2009),
            # 2010
            Date.westernStyle(20, Months.February, 2010),
            Date.westernStyle(21, Months.February, 2010),
            Date.westernStyle(12, Months.June, 2010),
            Date.westernStyle(13, Months.June, 2010),
            Date.westernStyle(19, Months.September, 2010),
            Date.westernStyle(25, Months.September, 2010),
            Date.westernStyle(26, Months.September, 2010),
            Date.westernStyle(9, Months.October, 2010),
            # 2011
            Date.westernStyle(30, Months.January, 2011),
            Date.westernStyle(12, Months.February, 2011),
            Date.westernStyle(2, Months.April, 2011),
            Date.westernStyle(8, Months.October, 2011),
            Date.westernStyle(9, Months.October, 2011),
            Date.westernStyle(31, Months.December, 2011),
            # 2012
            Date.westernStyle(21, Months.January, 2012),
            Date.westernStyle(29, Months.January, 2012),
            Date.westernStyle(31, Months.March, 2012),
            Date.westernStyle(1, Months.April, 2012),
            Date.westernStyle(28, Months.April, 2012),
            Date.westernStyle(29, Months.September, 2012),
            # 2013
            Date.westernStyle(5, Months.January,2013),
            Date.westernStyle(6, Months.January,2013),
            Date.westernStyle(16,Months.February,2013),
            Date.westernStyle(17,Months.February,2013),
            Date.westernStyle(7,Months.April,2013),
            Date.westernStyle(27,Months.April,2013),
            Date.westernStyle(28,Months.April,2013),
            Date.westernStyle(8,Months.June,2013),
            Date.westernStyle(9,Months.June,2013),
            Date.westernStyle(22,Months.September,2013),
            Date.westernStyle(29,Months.September,2013),
            Date.westernStyle(12,Months.October,2013),
            # 2014
            Date.westernStyle(26,Months.January,2014),
            Date.westernStyle(8,Months.February,2014),
            Date.westernStyle(4,Months.May,2014),
            Date.westernStyle(28,Months.September,2014),
            Date.westernStyle(11,Months.October,2014),
            # 2015
            Date.westernStyle(4,Months.January,2015),
            Date.westernStyle(15,Months.February,2015),
            Date.westernStyle(28,Months.February,2015),
			Date.westernStyle(6,Months.September,2015),
            Date.westernStyle(10,Months.October,2015)])

    def __init__(self):
        self._sseImpl = ChinaSseImpl()

    def isBizDay(self, date):
        return self._sseImpl.isBizDay(date) or date in ChinaIBImpl._working_weekends

    def isHoliday(self, d):
        return not self.isBizDay(d)

    def isWeekEnd(self, weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday


class NullCalendar(object):

    def __init__(self):
        pass

    def isBizDay(self, date):
        return True

    def isHoliday(self, date):
        return False

    def isWeekEnd(self, weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

_holDict = {'china.sse': ChinaSseImpl,
            'china.ib': ChinaIBImpl,
            'null': NullCalendar}