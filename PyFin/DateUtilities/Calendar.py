# -*- coding: utf-8 -*-
u"""
Created on 2015-7-9

@author: cheng.li
"""

from PyFin.Enums.Weekdays import Weekdays
from PyFin.Enums.Months import Months
from PyFin.Enums.BizDayConventions import BizDayConventions
from PyFin.Enums.TimeUnits import TimeUnits
from PyFin.DateUtilities.Date import Date
from PyFin.DateUtilities.Period import Period
from PyFin.Utilities import pyFinAssert


class Calendar(object):
    def __init__(self, holCenter):
        if isinstance(holCenter, str):
            holCenter = holCenter.lower()
            try:
                self._impl = _holDict[holCenter]()
            except KeyError:
                raise ValueError("{0} is not a valid description of a holiday center")
        else:
            raise ValueError("{0} is not a valid description of a holiday center")

    def isBizDay(self, d):
        return self._impl.isBizDay(d)

    def isHoliday(self, d):
        return not self.isBizDay(d)

    def isWeekEnd(self, weekday):
        return self._impl.isWeekEnd(weekday)

    def isEndOfMonth(self, d):
        return d.month() != self.adjustDate(d + 1).month()

    def endOfMonth(self, d):
        return self.adjustDate(Date.endOfMonth(d), BizDayConventions.Preceding)

    def bizDaysBetween(self, fromDate, toDate, includeFirst=True, includeLast=False):
        wd = 0
        if fromDate != toDate:
            if fromDate < toDate:
                d = fromDate
                while d < toDate:
                    if self.isBizDay(d):
                        wd += 1
                    d += 1
                if self.isBizDay(toDate):
                    wd += 1
            elif fromDate > toDate:
                d = toDate
                while d < fromDate:
                    if self.isBizDay(d):
                        wd += 1
                    d += 1
                if self.isBizDay(fromDate):
                    wd += 1
            if self.isBizDay(fromDate) and not includeFirst:
                wd -= 1
            if self.isBizDay(toDate) and not includeLast:
                wd -= 1
        return wd

    def adjustDate(self, d, c=BizDayConventions.Following):
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
            raise ValueError("unknown business-day convention")
        return d1

    def advanceDate(self, d, period, c=BizDayConventions.Following, endOfMonth=False):

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

    def holDatesList(self, fromDate, toDate, includeWeekEnds=True):
        pyFinAssert(fromDate <= toDate, ValueError, "from date ({0} must be earlier than to date {1}"
                 .format(fromDate, toDate))
        result = []
        d = fromDate
        while d <= toDate:
            if self.isHoliday(d) and (includeWeekEnds or not self.isWeekEnd(d.weekday())):
                result.append(d)
            d += 1
        return result

    def bizDatesList(self, fromDate, toDate):
        pyFinAssert(fromDate <= toDate, ValueError, "from date ({0} must be earlier than to date {1}"
                 .format(fromDate, toDate))
        result = []
        d = fromDate
        while d <= toDate:
            if self.isBizDay(d):
                result.append(d)
            d += 1
        return result

    def __eq__(self, right):
        return self._impl == right._impl


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
                or (y == 2004 and 19 <= d <= 28 and m == Months.January) \
                or (y == 2005 and 7 <= d <= 15 and m == Months.February) \
                or (y == 2006 and ((d >= 26 and m == Months.January) or (d <= 3 and m == Months.February))) \
                or (y == 2007 and 17 <= d <= 25 and m == Months.February) \
                or (y == 2008 and 6 <= d <= 12 and m == Months.February) \
                or (y == 2009 and 26 <= d <= 30 and m == Months.January) \
                or (y == 2010 and 15 <= d <= 19 and m == Months.February) \
                or (y == 2011 and 2 <= d <= 8 and m == Months.February) \
                or (y == 2012 and 23 <= d <= 28 and m == Months.January) \
                or (y == 2013 and 11 <= d <= 15 and m == Months.February) \
                or (y == 2014 and d >= 31 and m == Months.January) \
                or (y == 2014 and d <= 6 and m == Months.February) \
                or (y == 2015 and 18 <= d <= 24 and m == Months.February) \
                or (y <= 2008 and d == 4 and m == Months.April) \
                or (y == 2009 and d == 6 and m == Months.April) \
                or (y == 2010 and d == 5 and m == Months.April) \
                or (y == 2011 and 3 <= d <= 5 and m == Months.April) \
                or (y == 2012 and 2 <= d <= 4 and m == Months.April) \
                or (y == 2013 and 4 <= d <= 5 and m == Months.April) \
                or (y == 2014 and d == 7 and m == Months.April) \
                or (y == 2015 and 5 <= d <= 6 and m == Months.April) \
                or (y <= 2007 and 1 <= d <= 7 and m == Months.May) \
                or (y == 2008 and 1 <= d <= 2 and m == Months.May) \
                or (y == 2009 and d == 1 and m == Months.May) \
                or (y == 2010 and d == 3 and m == Months.May) \
                or (y == 2011 and d == 2 and m == Months.May) \
                or (y == 2012 and ((d == 30 and m == Months.April) or (d == 1 and m == Months.May))) \
                or (y == 2013 and ((d >= 29 and m == Months.April) or (d == 1 and m == Months.May))) \
                or (y == 2014 and 1 <= d <= 3 and m == Months.May) \
                or (y == 2015 and d == 1 and m == Months.May) \
                or (y <= 2008 and d == 9 and m == Months.June) \
                or (y == 2009 and (d == 28 or d == 29) and m == Months.May) \
                or (y == 2010 and 14 <= d <= 16 and m == Months.June) \
                or (y == 2011 and 4 <= d <= 6 and m == Months.June) \
                or (y == 2012 and 22 <= d <= 24 and m == Months.June) \
                or (y == 2013 and 10 <= d <= 12 and m == Months.June) \
                or (y == 2014 and d == 2 and m == Months.June) \
                or (y == 2015 and d == 22 and m == Months.June) \
                or (y <= 2008 and d == 15 and m == Months.September) \
                or (y == 2010 and 22 <= d <= 24 and m == Months.September) \
                or (y == 2011 and 10 <= d <= 12 and m == Months.September) \
                or (y == 2012 and d == 30 and m == Months.September) \
                or (y == 2013 and 19 <= d <= 20 and m == Months.September) \
                or (y == 2014 and d == 8 and m == Months.September) \
                or (y == 2015 and d == 27 and m == Months.September) \
                or (y <= 2007 and 1 <= d <= 7 and m == Months.October) \
                or (y == 2008 and ((d >= 29 and m == Months.September) or (d <= 3 and m == Months.October))) \
                or (y == 2009 and 1 <= d <= 8 and m == Months.October) \
                or (y == 2010 and 1 <= d <= 7 and m == Months.October) \
                or (y == 2011 and 1 <= d <= 7 and m == Months.October) \
                or (y == 2012 and 1 <= d <= 7 and m == Months.October) \
                or (y == 2013 and 1 <= d <= 7 and m == Months.October) \
                or (y == 2014 and 1 <= d <= 7 and m == Months.October) \
                or (y == 2015 and 1 <= d <= 7 and m == Months.October) \
                or (y == 2015 and 3 <= d <= 4 and m == Months.September):
            return False
        return True

    def isWeekEnd(self, weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    def __eq__(self, right):
        if isinstance(right, ChinaSseImpl):
            return True
        else:
            return False


class ChinaIBImpl(object):
    _working_weekends = {
        # 2005
        Date.westernStyle(5, Months.February, 2005),
        Date.westernStyle(6, Months.February, 2005),
        Date.westernStyle(30, Months.April, 2005),
        Date.westernStyle(8, Months.May, 2005),
        Date.westernStyle(8, Months.October, 2005),
        Date.westernStyle(9, Months.October, 2005),
        Date.westernStyle(31, Months.December, 2005),
        # 2006
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
        Date.westernStyle(5, Months.January, 2013),
        Date.westernStyle(6, Months.January, 2013),
        Date.westernStyle(16, Months.February, 2013),
        Date.westernStyle(17, Months.February, 2013),
        Date.westernStyle(7, Months.April, 2013),
        Date.westernStyle(27, Months.April, 2013),
        Date.westernStyle(28, Months.April, 2013),
        Date.westernStyle(8, Months.June, 2013),
        Date.westernStyle(9, Months.June, 2013),
        Date.westernStyle(22, Months.September, 2013),
        Date.westernStyle(29, Months.September, 2013),
        Date.westernStyle(12, Months.October, 2013),
        # 2014
        Date.westernStyle(26, Months.January, 2014),
        Date.westernStyle(8, Months.February, 2014),
        Date.westernStyle(4, Months.May, 2014),
        Date.westernStyle(28, Months.September, 2014),
        Date.westernStyle(11, Months.October, 2014),
        # 2015
        Date.westernStyle(4, Months.January, 2015),
        Date.westernStyle(15, Months.February, 2015),
        Date.westernStyle(28, Months.February, 2015),
        Date.westernStyle(6, Months.September, 2015),
        Date.westernStyle(10, Months.October, 2015)
    }

    def __init__(self):
        self._sseImpl = ChinaSseImpl()

    def isBizDay(self, date):
        return self._sseImpl.isBizDay(date) or date in ChinaIBImpl._working_weekends

    def isWeekEnd(self, weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    def __eq__(self, right):
        if isinstance(right, ChinaIBImpl):
            return True
        else:
            return False


class NullCalendar(object):
    def __init__(self):
        pass

    def isBizDay(self, date):
        return True

    def isWeekEnd(self, weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    def __eq__(self, right):
        if isinstance(right, NullCalendar):
            return True
        else:
            return False


class WestenImpl(object):
    EasterMonday = [
        98, 90, 103, 95, 114, 106, 91, 111, 102,  # 1901-1909
        87, 107, 99, 83, 103, 95, 115, 99, 91, 111,  # 1910-1919
        96, 87, 107, 92, 112, 103, 95, 108, 100, 91,  # 1920-1929
        111, 96, 88, 107, 92, 112, 104, 88, 108, 100,  # 1930-1939
        85, 104, 96, 116, 101, 92, 112, 97, 89, 108,  # 1940-1949
        100, 85, 105, 96, 109, 101, 93, 112, 97, 89,  # 1950-1959
        109, 93, 113, 105, 90, 109, 101, 86, 106, 97,  # 1960-1969
        89, 102, 94, 113, 105, 90, 110, 101, 86, 106,  # 1970-1979
        98, 110, 102, 94, 114, 98, 90, 110, 95, 86,  # 1980-1989
        106, 91, 111, 102, 94, 107, 99, 90, 103, 95,  # 1990-1999
        115, 106, 91, 111, 103, 87, 107, 99, 84, 103,  # 2000-2009
        95, 115, 100, 91, 111, 96, 88, 107, 92, 112,  # 2010-2019
        104, 95, 108, 100, 92, 111, 96, 88, 108, 92,  # 2020-2029
        112, 104, 89, 108, 100, 85, 105, 96, 116, 101,  # 2030-2039
        93, 112, 97, 89, 109, 100, 85, 105, 97, 109,  # 2040-2049
        101, 93, 113, 97, 89, 109, 94, 113, 105, 90,  # 2050-2059
        110, 101, 86, 106, 98, 89, 102, 94, 114, 105,  # 2060-2069
        90, 110, 102, 86, 106, 98, 111, 102, 94, 114,  # 2070-2079
        99, 90, 110, 95, 87, 106, 91, 111, 103, 94,  # 2080-2089
        107, 99, 91, 103, 95, 115, 107, 91, 111, 103,  # 2090-2099
        88, 108, 100, 85, 105, 96, 109, 101, 93, 112,  # 2100-2109
        97, 89, 109, 93, 113, 105, 90, 109, 101, 86,  # 2110-2119
        106, 97, 89, 102, 94, 113, 105, 90, 110, 101,  # 2120-2129
        86, 106, 98, 110, 102, 94, 114, 98, 90, 110,  # 2130-2139
        95, 86, 106, 91, 111, 102, 94, 107, 99, 90,  # 2140-2149
        103, 95, 115, 106, 91, 111, 103, 87, 107, 99,  # 2150-2159
        84, 103, 95, 115, 100, 91, 111, 96, 88, 107,  # 2160-2169
        92, 112, 104, 95, 108, 100, 92, 111, 96, 88,  # 2170-2179
        108, 92, 112, 104, 89, 108, 100, 85, 105, 96,  # 2180-2189
        116, 101, 93, 112, 97, 89, 109, 100, 85, 105  # 2190-2199
    ]

    def isWeekEnd(self, weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    @classmethod
    def easterMonday(cls, year):
        return cls.EasterMonday[year - 1901]


class TargetImpl(WestenImpl):
    def __init__(self):
        pass

    def isBizDay(self, date):
        w = date.weekday()
        d = date.dayOfMonth()
        dd = date.dayOfYear()
        m = date.month()
        y = date.year()
        em = self.easterMonday(y)

        if (self.isWeekEnd(w)
            or (d == 1 and m == Months.January)
            or (dd == em - 3 and y >= 2000)
            or (dd == em and y >= 2000)
            or (d == 1 and m == Months.May and y >= 2000)
            or (d == 25 and m == Months.December)
            or (d == 26 and m == Months.December and y >= 2000)
            or (d == 31 and m == Months.December and (y == 1998 or y == 1999 or y == 2001))):
            return False
        return True

    def __eq__(self, right):
        if isinstance(right, TargetImpl):
            return True
        else:
            return False


_holDict = {'china.sse': ChinaSseImpl,
            'china.ib': ChinaIBImpl,
            'target': TargetImpl,
            'null': NullCalendar,
            'nullcalendar': NullCalendar}
