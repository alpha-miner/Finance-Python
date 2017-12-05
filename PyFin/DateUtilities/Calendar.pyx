# -*- coding: utf-8 -*-
u"""
Created on 2017-2-1

@author: cheng.li
"""

from PyFin.Enums._Weekdays cimport Weekdays
from PyFin.Enums._TimeUnits cimport TimeUnits
from PyFin.Enums._Months cimport Months
from PyFin.Enums._BizDayConventions cimport BizDayConventions
from PyFin.DateUtilities.Date cimport Date
from PyFin.DateUtilities.Period cimport Period

cdef class Calendar(object):
    def __init__(self, str holCenter):
        holCenter = holCenter.lower()
        try:
            self._impl = _holDict[holCenter]()
        except KeyError:
            raise ValueError("{0} is not a valid description of a holiday center".format(holCenter))
        self.name = holCenter

    cpdef isBizDay(self, Date d):
        return self._impl.isBizDay(d)

    cpdef isHoliday(self, Date d):
        return not self._impl.isBizDay(d)

    cpdef isWeekEnd(self, int weekday):
        return self._impl.isWeekEnd(weekday)

    cpdef isEndOfMonth(self, Date d):
        return d.month() != self.adjustDate(d + 1).month()

    cpdef endOfMonth(self, Date d):
        return self.adjustDate(Date.endOfMonth(d), BizDayConventions.Preceding)

    cpdef bizDaysBetween(self, Date fromDate, Date toDate, bint includeFirst=True, bint includeLast=False):
        cdef int wd = 0
        cdef Date d

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

    cpdef adjustDate(self, Date d, int c=BizDayConventions.Following):

        cdef Date d1
        cdef Date d2

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
                    if d.dayOfMonth() <= 15 < d1.dayOfMonth():
                        return self.adjustDate(d, BizDayConventions.Preceding)
        elif c == BizDayConventions.Preceding or c == BizDayConventions.ModifiedPreceding:
            while self.isHoliday(d1):
                d1 -= 1
            if c == BizDayConventions.ModifiedPreceding and d1.month() != d.month():
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

    cpdef advanceDate(self, Date d, Period period, int c=BizDayConventions.Following, bint endOfMonth=False):

        cdef int n
        cdef int units
        cdef Date d1

        n = period.length()
        units = period.units()

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

    cpdef holDatesList(self, Date fromDate, Date toDate, bint includeWeekEnds=True):
        cdef list result = []
        cdef Date d = fromDate

        while d <= toDate:
            if self.isHoliday(d) and (includeWeekEnds or not self.isWeekEnd(d.weekday())):
                result.append(d)
            d += 1
        return result

    cpdef bizDatesList(self, Date fromDate, Date toDate):
        cdef list result = []
        cdef Date d = fromDate

        while d <= toDate:
            if self.isBizDay(d):
                result.append(d)
            d += 1
        return result

    def __richcmp__(self, right, int op):
        if op == 2:
            return self._impl == right._impl

    def __deepcopy__(self, memo):
        return Calendar(self.name)

    def __reduce__(self):
        d = {}

        return Calendar, (self.name,), d

    def __setstate__(self, state):
        pass

cdef class CalendarImpl(object):
    cdef bint isBizDay(self, Date date):
        pass

    cdef bint isWeekEnd(self, int weekDay):
        pass

cdef set sse_holDays = {Date(2005, 1, 3),
                        Date(2005, 2, 7),
                        Date(2005, 2, 8),
                        Date(2005, 2, 9),
                        Date(2005, 2, 10),
                        Date(2005, 2, 11),
                        Date(2005, 2, 14),
                        Date(2005, 2, 15),
                        Date(2005, 4, 4),
                        Date(2005, 5, 2),
                        Date(2005, 5, 3),
                        Date(2005, 5, 4),
                        Date(2005, 5, 5),
                        Date(2005, 5, 6),
                        Date(2005, 6, 9),
                        Date(2005, 9, 15),
                        Date(2005, 10, 3),
                        Date(2005, 10, 4),
                        Date(2005, 10, 5),
                        Date(2005, 10, 6),
                        Date(2005, 10, 7),
                        Date(2006, 1, 2),
                        Date(2006, 1, 3),
                        Date(2006, 1, 26),
                        Date(2006, 1, 27),
                        Date(2006, 1, 30),
                        Date(2006, 1, 31),
                        Date(2006, 2, 1),
                        Date(2006, 2, 2),
                        Date(2006, 2, 3),
                        Date(2006, 4, 4),
                        Date(2006, 5, 1),
                        Date(2006, 5, 2),
                        Date(2006, 5, 3),
                        Date(2006, 5, 4),
                        Date(2006, 5, 5),
                        Date(2006, 6, 9),
                        Date(2006, 9, 15),
                        Date(2006, 10, 2),
                        Date(2006, 10, 3),
                        Date(2006, 10, 4),
                        Date(2006, 10, 5),
                        Date(2006, 10, 6),
                        Date(2007, 1, 1),
                        Date(2007, 1, 2),
                        Date(2007, 1, 3),
                        Date(2007, 2, 19),
                        Date(2007, 2, 20),
                        Date(2007, 2, 21),
                        Date(2007, 2, 22),
                        Date(2007, 2, 23),
                        Date(2007, 4, 4),
                        Date(2007, 5, 1),
                        Date(2007, 5, 2),
                        Date(2007, 5, 3),
                        Date(2007, 5, 4),
                        Date(2007, 5, 7),
                        Date(2007, 10, 1),
                        Date(2007, 10, 2),
                        Date(2007, 10, 3),
                        Date(2007, 10, 4),
                        Date(2007, 10, 5),
                        Date(2007, 12, 31),
                        Date(2008, 1, 1),
                        Date(2008, 2, 6),
                        Date(2008, 2, 7),
                        Date(2008, 2, 8),
                        Date(2008, 2, 11),
                        Date(2008, 2, 12),
                        Date(2008, 4, 4),
                        Date(2008, 5, 1),
                        Date(2008, 5, 2),
                        Date(2008, 6, 9),
                        Date(2008, 9, 15),
                        Date(2008, 9, 29),
                        Date(2008, 9, 30),
                        Date(2008, 10, 1),
                        Date(2008, 10, 2),
                        Date(2008, 10, 3),
                        Date(2009, 1, 1),
                        Date(2009, 1, 2),
                        Date(2009, 1, 26),
                        Date(2009, 1, 27),
                        Date(2009, 1, 28),
                        Date(2009, 1, 29),
                        Date(2009, 1, 30),
                        Date(2009, 4, 6),
                        Date(2009, 5, 1),
                        Date(2009, 5, 28),
                        Date(2009, 5, 29),
                        Date(2009, 10, 1),
                        Date(2009, 10, 2),
                        Date(2009, 10, 5),
                        Date(2009, 10, 6),
                        Date(2009, 10, 7),
                        Date(2009, 10, 8),
                        Date(2010, 1, 1),
                        Date(2010, 2, 15),
                        Date(2010, 2, 16),
                        Date(2010, 2, 17),
                        Date(2010, 2, 18),
                        Date(2010, 2, 19),
                        Date(2010, 4, 5),
                        Date(2010, 5, 3),
                        Date(2010, 6, 14),
                        Date(2010, 6, 15),
                        Date(2010, 6, 16),
                        Date(2010, 9, 22),
                        Date(2010, 9, 23),
                        Date(2010, 9, 24),
                        Date(2010, 10, 1),
                        Date(2010, 10, 4),
                        Date(2010, 10, 5),
                        Date(2010, 10, 6),
                        Date(2010, 10, 7),
                        Date(2011, 1, 3),
                        Date(2011, 2, 2),
                        Date(2011, 2, 3),
                        Date(2011, 2, 4),
                        Date(2011, 2, 7),
                        Date(2011, 2, 8),
                        Date(2011, 4, 4),
                        Date(2011, 4, 5),
                        Date(2011, 5, 2),
                        Date(2011, 6, 6),
                        Date(2011, 9, 12),
                        Date(2011, 10, 3),
                        Date(2011, 10, 4),
                        Date(2011, 10, 5),
                        Date(2011, 10, 6),
                        Date(2011, 10, 7),
                        Date(2012, 1, 2),
                        Date(2012, 1, 3),
                        Date(2012, 1, 23),
                        Date(2012, 1, 24),
                        Date(2012, 1, 25),
                        Date(2012, 1, 26),
                        Date(2012, 1, 27),
                        Date(2012, 4, 2),
                        Date(2012, 4, 3),
                        Date(2012, 4, 4),
                        Date(2012, 4, 30),
                        Date(2012, 5, 1),
                        Date(2012, 6, 22),
                        Date(2012, 10, 1),
                        Date(2012, 10, 2),
                        Date(2012, 10, 3),
                        Date(2012, 10, 4),
                        Date(2012, 10, 5),
                        Date(2013, 1, 1),
                        Date(2013, 1, 2),
                        Date(2013, 1, 3),
                        Date(2013, 2, 11),
                        Date(2013, 2, 12),
                        Date(2013, 2, 13),
                        Date(2013, 2, 14),
                        Date(2013, 2, 15),
                        Date(2013, 4, 4),
                        Date(2013, 4, 5),
                        Date(2013, 4, 29),
                        Date(2013, 4, 30),
                        Date(2013, 5, 1),
                        Date(2013, 6, 10),
                        Date(2013, 6, 11),
                        Date(2013, 6, 12),
                        Date(2013, 9, 19),
                        Date(2013, 9, 20),
                        Date(2013, 10, 1),
                        Date(2013, 10, 2),
                        Date(2013, 10, 3),
                        Date(2013, 10, 4),
                        Date(2013, 10, 7),
                        Date(2014, 1, 1),
                        Date(2014, 1, 31),
                        Date(2014, 2, 3),
                        Date(2014, 2, 4),
                        Date(2014, 2, 5),
                        Date(2014, 2, 6),
                        Date(2014, 4, 7),
                        Date(2014, 5, 1),
                        Date(2014, 5, 2),
                        Date(2014, 6, 2),
                        Date(2014, 9, 8),
                        Date(2014, 10, 1),
                        Date(2014, 10, 2),
                        Date(2014, 10, 3),
                        Date(2014, 10, 6),
                        Date(2014, 10, 7),
                        Date(2015, 1, 1),
                        Date(2015, 1, 2),
                        Date(2015, 2, 18),
                        Date(2015, 2, 19),
                        Date(2015, 2, 20),
                        Date(2015, 2, 23),
                        Date(2015, 2, 24),
                        Date(2015, 4, 6),
                        Date(2015, 5, 1),
                        Date(2015, 6, 22),
                        Date(2015, 9, 3),
                        Date(2015, 9, 4),
                        Date(2015, 10, 1),
                        Date(2015, 10, 2),
                        Date(2015, 10, 5),
                        Date(2015, 10, 6),
                        Date(2015, 10, 7),
                        Date(2016, 1, 1),
                        Date(2016, 2, 8),
                        Date(2016, 2, 9),
                        Date(2016, 2, 10),
                        Date(2016, 2, 11),
                        Date(2016, 2, 12),
                        Date(2016, 4, 4),
                        Date(2016, 5, 1),
                        Date(2016, 5, 2),
                        Date(2016, 6, 9),
                        Date(2016, 6, 10),
                        Date(2016, 9, 15),
                        Date(2016, 9, 16),
                        Date(2016, 10, 3),
                        Date(2016, 10, 4),
                        Date(2016, 10, 5),
                        Date(2016, 10, 6),
                        Date(2016, 10, 7),
                        Date(2017, 1, 2),
                        Date(2017, 1, 27),
                        Date(2017, 1, 30),
                        Date(2017, 1, 31),
                        Date(2017, 2, 1),
                        Date(2017, 2, 2),
                        Date(2017, 4, 3),
                        Date(2017, 4, 4),
                        Date(2017, 5, 1),
                        Date(2017, 5, 29),
                        Date(2017, 5, 30),
                        Date(2017, 10, 2),
                        Date(2017, 10, 3),
                        Date(2017, 10, 4),
                        Date(2017, 10, 5),
                        Date(2017, 10, 6),
                        Date(2018, 1, 1),
                        Date(2018, 2, 15),
                        Date(2018, 2, 16),
                        Date(2018, 2, 19),
                        Date(2018, 2, 20),
                        Date(2018, 2, 21),
                        Date(2018, 4, 5),
                        Date(2018, 4, 6),
                        Date(2018, 4, 30),
                        Date(2018, 5, 1),
                        Date(2018, 6, 18),
                        Date(2018, 9, 24),
                        Date(2018, 10, 1),
                        Date(2018, 10, 2),
                        Date(2018, 10, 3),
                        Date(2018, 10, 4),
                        Date(2018, 10, 5)}

cdef class ChinaSseImpl(CalendarImpl):
    def __init__(self):
        pass

    cdef bint isBizDay(self, Date date):
        cdef int w = date.weekday()
        if self.isWeekEnd(w) or date in sse_holDays:
            return False
        return True

    cdef bint isWeekEnd(self, int weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    def __richcmp__(self, right, int op):
        if op == 2:
            return isinstance(right, ChinaSseImpl)

cdef set ib_working_weekends = {
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
    Date.westernStyle(10, Months.October, 2015),
    # 2016
    Date.westernStyle(6, Months.February, 2016),
    Date.westernStyle(14, Months.February, 2016),
    Date.westernStyle(12, Months.June, 2016),
    Date.westernStyle(18, Months.September, 2016),
    Date.westernStyle(8, Months.October, 2016),
    Date.westernStyle(9, Months.October, 2016),
    # 2017
    Date.westernStyle(22, Months.January, 2017),
    Date.westernStyle(4, Months.February, 2017),
    Date.westernStyle(1, Months.April, 2017),
    Date.westernStyle(27, Months.May, 2017),
    Date.westernStyle(30, Months.September, 2017),
    # 2018
    Date.westernStyle(11, Months.February, 2018),
    Date.westernStyle(24, Months.February, 2018),
    Date.westernStyle(8, Months.April, 2018),
    Date.westernStyle(28, Months.April, 2018),
    Date.westernStyle(29, Months.September, 2018),
    Date.westernStyle(30, Months.September, 2018),
}

cdef ChinaSseImpl _sseImpl = ChinaSseImpl()

cdef class ChinaIBImpl(CalendarImpl):
    def __init__(self):
        pass

    cpdef bint isBizDay(self, Date date):
        return _sseImpl.isBizDay(date) or date in ib_working_weekends

    cpdef bint isWeekEnd(self, int weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    def __richcmp__(self, right, int op):
        if op == 2:
            return isinstance(right, ChinaIBImpl)

cdef class NullCalendar(CalendarImpl):
    def __init__(self):
        pass

    cdef bint isBizDay(self, Date date):
        return True

    cdef bint isWeekEnd(self, int weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    def __richcmp__(self, right, int op):
        if op == 2:
            return isinstance(right, NullCalendar)

cdef class ChinaCFFEXImpl(CalendarImpl):
    def __init__(self):
        pass

    cdef bint isBizDay(self, Date date):
        return _sseImpl.isBizDay(date)

    cdef bint isWeekEnd(self, int weekDay):
        return _sseImpl.isWeekEnd(weekDay)

    def __richcmp__(self, right, int op):
        if op == 2:
            return isinstance(right, ChinaCFFEXImpl)

cdef int EasterMonday[299]
EasterMonday[:] = [
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

cdef class WestenImpl(CalendarImpl):
    cdef bint isWeekEnd(self, int weekDay):
        return weekDay == Weekdays.Saturday or weekDay == Weekdays.Sunday

    cdef int easterMonday(self, int year):
        return EasterMonday[year - 1901]

cdef class TargetImpl(WestenImpl):
    def __init__(self):
        pass

    cdef bint isBizDay(self, Date date):
        cdef int w = date.weekday()
        cdef int d = date.dayOfMonth()
        cdef int dd = date.dayOfYear()
        cdef int m = date.month()
        cdef int y = date.year()
        cdef int em = self.easterMonday(y)

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

    def __richcmp__(self, right, int op):
        if op == 2:
            return isinstance(right, TargetImpl)

cdef dict _holDict = {'china.sse': ChinaSseImpl,
                      'china.ib': ChinaIBImpl,
                      'china.cffex': ChinaCFFEXImpl,
                      'target': TargetImpl,
                      'null': NullCalendar,
                      'nullcalendar': NullCalendar}
