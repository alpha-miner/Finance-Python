# -*- coding: utf-8 -*-
u"""
Created on 2015-7-9

@author: cheng.li
"""

import datetime as dt
import math
from PyFin.Enums.TimeUnits import TimeUnits
from PyFin.DateUtilities.Period import Period
from PyFin.Enums.Weekdays import Weekdays
from PyFin.Utilities import pyFinAssert


class Date(object):
    def __init__(self, year=None, month=None, day=None, serialNumber=None):
        # do the input validation
        if serialNumber is not None and year is None and month is None and day is None:
            self.__serialNumber__ = serialNumber
            return
        elif serialNumber is not None and (year is not None or month is not None or day is not None):
            raise ValueError("When serial number is offered, no year or month or day number should be entered")
        elif year is None or month is None or day is None:
            raise ValueError("year: {0}, month: {1}, day: {2} can't be null value included".format(year, month, day))

        isLeap = self.isLeap(year)

        pyFinAssert(1 <= month <= 12, ValueError, 'month {0:d} is out of bound. It must be in [1, 12]'.format(month))

        length = self._monthLength(month, isLeap)
        offset = self._monthOffset(month, isLeap)

        pyFinAssert(1 <= day <= length, ValueError, 'day {0:d} is out of bound. It must be in [1, {1:d}]'
                 .format(day, length))

        self.__serialNumber__ = day + offset + _YearOffset[year - 1900]

    def dayOfMonth(self):
        return self.dayOfYear() - self._monthOffset(self.month(), self.isLeap(self.year()))

    def dayOfYear(self):
        return self.__serialNumber__ - _YearOffset[self.year() - 1900]

    def year(self):
        y = (int(self.__serialNumber__ / 365)) + 1900
        if self.__serialNumber__ <= _YearOffset[y - 1900]:
            return y - 1
        return y

    def month(self):
        d = self.dayOfYear()
        m = int(d / 30) + 1
        leap = self.isLeap(self.year())
        while d <= self._monthOffset(m, leap):
            m -= 1
        return m

    def weekday(self):
        w = self.__serialNumber__ % 7
        return Weekdays(7 if w == 0 else w)

    def toDateTime(self):
        return dt.date(self.year(), self.month(), self.dayOfMonth())

    @property
    def serialNumber(self):
        return self.__serialNumber__

    def __eq__(self, other):
        return self.__serialNumber__ == other.__serialNumber__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.__serialNumber__ <= other.__serialNumber__

    def __lt__(self, other):
        return self.__serialNumber__ < other.__serialNumber__

    def __ge__(self, other):
        return not self.__lt__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __add__(self, period):
        if isinstance(period, Period):
            return Date._advance(self, period.length, period.units)
        elif isinstance(period, int):
            return Date._advance(self, period, TimeUnits.Days)
        else:
            period = Period(period)
            return Date._advance(self, period.length, period.units)

    def __sub__(self, period):
        if isinstance(period, Period):
            return Date._advance(self, -period.length, period.units)
        elif isinstance(period, int):
            return Date._advance(self, -period, TimeUnits.Days)
        elif isinstance(period, Date):
            return self.__serialNumber__ - period.serialNumber
        else:
            period = Period(period)
            return Date._advance(self, -period.length, period.units)

    def __hash__(self):
        return self.__serialNumber__

    def __str__(self):
        d = self.dayOfMonth()
        m = self.month()
        y = self.year()
        return "{0:d}-{1:02d}-{2:02d}".format(y, m, d)

    def __repr__(self):
        d = self.dayOfMonth()
        m = self.month()
        y = self.year()
        return "Date({0:d}, {1:d}, {2:d})".format(y, m, d)

    @staticmethod
    def minDate():
        return Date(1901, 1, 1)

    @staticmethod
    def maxDate():
        return Date(2199, 12, 31)

    @staticmethod
    def endOfMonth(date):
        m = date.month()
        y = date.year()
        return Date(y, m, Date._monthLength(m, Date.isLeap(y)))

    @staticmethod
    def isEndOfMonth(date):
        m = date.month()
        y = date.year()
        return date.dayOfMonth() == Date._monthLength(m, Date.isLeap(y))

    @staticmethod
    def nextWeekday(date, dayOfWeek):
        wd = date.weekday()
        return date + ((7 if wd > dayOfWeek else 0) - wd + dayOfWeek)

    @staticmethod
    def nthWeekday(nth, dayOfWeek, m, y):
        pyFinAssert(nth > 0, ValueError, "zeroth day of week in a given (month, year) is undefined")
        pyFinAssert(nth < 6, ValueError, "no more than 5 weekday in a given (month, year)")

        first = Date(y, m, 1).weekday()
        skip = nth - (1 if dayOfWeek >= first else 0)
        return Date(y, m, (1 + dayOfWeek + skip * 7) - first)

    @classmethod
    def todaysDate(cls):
        today = dt.date.today()
        return cls(today.year, today.month, today.day)

    @staticmethod
    def isLeap(year):
        pyFinAssert(1900 < year < 2200, ValueError, 'year {0:d} is out of bound. It must be in [1901, 2199]'.format(year))
        return _YearIsLeap[year - 1900]

    @staticmethod
    def _monthLength(month, isLeap):
        if isLeap:
            return _MonthLeapLength[month - 1]
        else:
            return _MonthLength[month - 1]

    @staticmethod
    def _monthOffset(month, isLeap):
        if isLeap:
            return _MonthLeapOffset[month - 1]
        else:
            return _MonthOffset[month - 1]

    @classmethod
    def fromExcelSerialNumber(cls, serialNumber):
        return cls(serialNumber=serialNumber)

    @classmethod
    def fromDateTime(cls, dateTime):
        return cls(dateTime.year, dateTime.month, dateTime.day)

    @classmethod
    def parseISO(cls, dateStr):
        pyFinAssert(len(dateStr) == 10 and dateStr[4] == '-' and dateStr[7] == '-', ValueError,
                 "invalid format {0}".format(dateStr))
        return cls(int(dateStr[0:4]), int(dateStr[5:7]), int(dateStr[8:10]))

    @classmethod
    def strptime(cls, dateStr, dateFormat='%Y-%m-%d'):
        pydt = dt.datetime.strptime(dateStr, dateFormat)
        return cls(pydt.year, pydt.month, pydt.day)

    @classmethod
    def _advance(cls, date, n, units):
        if units == TimeUnits.Days or units == TimeUnits.BDays:
            return cls.fromExcelSerialNumber(date.__serialNumber__ + n)
        elif units == TimeUnits.Weeks:
            return cls.fromExcelSerialNumber(date.__serialNumber__ + 7 * n)
        elif units == TimeUnits.Months:
            d = date.dayOfMonth()
            m = date.month() + n
            y = date.year()
            addedYear = int(math.floor(m / 12))
            monthLeft = m % 12
            if monthLeft == 0:
                monthLeft = 12
                addedYear -= 1
            y += addedYear

            pyFinAssert(1900 < y < 2200, ValueError, 'year {0:d} is out of bound. It must be in [1901, 2199]'.format(y))

            return cls(y, monthLeft, d)
        elif units == TimeUnits.Years:
            d = date.dayOfMonth()
            m = date.month()
            y = date.year() + n

            pyFinAssert(1900 < y < 2200, ValueError, 'year {0:d} is out of bound. It must be in [1901, 2199]'.format(y))

            return cls(y, m, d)

    @classmethod
    def westernStyle(cls, day, month, year):
        return cls(year, month, day)


_YearIsLeap = [
    # 1900 is leap in agreement with Excel's bug
    # 1900 is out of valid date range anyway
    # 1900-1909
    True, False, False, False, True, False, False, False, True, False,
    # 1910-1919
    False, False, True, False, False, False, True, False, False, False,
    # 1920-1929
    True, False, False, False, True, False, False, False, True, False,
    # 1930-1939
    False, False, True, False, False, False, True, False, False, False,
    # 1940-1949
    True, False, False, False, True, False, False, False, True, False,
    # 1950-1959
    False, False, True, False, False, False, True, False, False, False,
    # 1960-1969
    True, False, False, False, True, False, False, False, True, False,
    # 1970-1979
    False, False, True, False, False, False, True, False, False, False,
    # 1980-1989
    True, False, False, False, True, False, False, False, True, False,
    # 1990-1999
    False, False, True, False, False, False, True, False, False, False,
    # 2000-2009
    True, False, False, False, True, False, False, False, True, False,
    # 2010-2019
    False, False, True, False, False, False, True, False, False, False,
    # 2020-2029
    True, False, False, False, True, False, False, False, True, False,
    # 2030-2039
    False, False, True, False, False, False, True, False, False, False,
    # 2040-2049
    True, False, False, False, True, False, False, False, True, False,
    # 2050-2059
    False, False, True, False, False, False, True, False, False, False,
    # 2060-2069
    True, False, False, False, True, False, False, False, True, False,
    # 2070-2079
    False, False, True, False, False, False, True, False, False, False,
    # 2080-2089
    True, False, False, False, True, False, False, False, True, False,
    # 2090-2099
    False, False, True, False, False, False, True, False, False, False,
    # 2100-2109
    False, False, False, False, True, False, False, False, True, False,
    # 2110-2119
    False, False, True, False, False, False, True, False, False, False,
    # 2120-2129
    True, False, False, False, True, False, False, False, True, False,
    # 2130-2139
    False, False, True, False, False, False, True, False, False, False,
    # 2140-2149
    True, False, False, False, True, False, False, False, True, False,
    # 2150-2159
    False, False, True, False, False, False, True, False, False, False,
    # 2160-2169
    True, False, False, False, True, False, False, False, True, False,
    # 2170-2179
    False, False, True, False, False, False, True, False, False, False,
    # 2180-2189
    True, False, False, False, True, False, False, False, True, False,
    # 2190-2199
    False, False, True, False, False, False, True, False, False, False,
    # 2200
    False
]

_YearOffset = [
    # 1900-1909
    0, 366, 731, 1096, 1461, 1827, 2192, 2557, 2922, 3288,
    # 1910-1919
    3653, 4018, 4383, 4749, 5114, 5479, 5844, 6210, 6575, 6940,
    # 1920-1929
    7305, 7671, 8036, 8401, 8766, 9132, 9497, 9862, 10227, 10593,
    # 1930-1939
    10958, 11323, 11688, 12054, 12419, 12784, 13149, 13515, 13880, 14245,
    # 1940-1949
    14610, 14976, 15341, 15706, 16071, 16437, 16802, 17167, 17532, 17898,
    # 1950-1959
    18263, 18628, 18993, 19359, 19724, 20089, 20454, 20820, 21185, 21550,
    # 1960-1969
    21915, 22281, 22646, 23011, 23376, 23742, 24107, 24472, 24837, 25203,
    # 1970-1979
    25568, 25933, 26298, 26664, 27029, 27394, 27759, 28125, 28490, 28855,
    # 1980-1989
    29220, 29586, 29951, 30316, 30681, 31047, 31412, 31777, 32142, 32508,
    # 1990-1999
    32873, 33238, 33603, 33969, 34334, 34699, 35064, 35430, 35795, 36160,
    # 2000-2009
    36525, 36891, 37256, 37621, 37986, 38352, 38717, 39082, 39447, 39813,
    # 2010-2019
    40178, 40543, 40908, 41274, 41639, 42004, 42369, 42735, 43100, 43465,
    # 2020-2029
    43830, 44196, 44561, 44926, 45291, 45657, 46022, 46387, 46752, 47118,
    # 2030-2039
    47483, 47848, 48213, 48579, 48944, 49309, 49674, 50040, 50405, 50770,
    # 2040-2049
    51135, 51501, 51866, 52231, 52596, 52962, 53327, 53692, 54057, 54423,
    # 2050-2059
    54788, 55153, 55518, 55884, 56249, 56614, 56979, 57345, 57710, 58075,
    # 2060-2069
    58440, 58806, 59171, 59536, 59901, 60267, 60632, 60997, 61362, 61728,
    # 2070-2079
    62093, 62458, 62823, 63189, 63554, 63919, 64284, 64650, 65015, 65380,
    # 2080-2089
    65745, 66111, 66476, 66841, 67206, 67572, 67937, 68302, 68667, 69033,
    # 2090-2099
    69398, 69763, 70128, 70494, 70859, 71224, 71589, 71955, 72320, 72685,
    # 2100-2109
    73050, 73415, 73780, 74145, 74510, 74876, 75241, 75606, 75971, 76337,
    # 2110-2119
    76702, 77067, 77432, 77798, 78163, 78528, 78893, 79259, 79624, 79989,
    # 2120-2129
    80354, 80720, 81085, 81450, 81815, 82181, 82546, 82911, 83276, 83642,
    # 2130-2139
    84007, 84372, 84737, 85103, 85468, 85833, 86198, 86564, 86929, 87294,
    # 2140-2149
    87659, 88025, 88390, 88755, 89120, 89486, 89851, 90216, 90581, 90947,
    # 2150-2159
    91312, 91677, 92042, 92408, 92773, 93138, 93503, 93869, 94234, 94599,
    # 2160-2169
    94964, 95330, 95695, 96060, 96425, 96791, 97156, 97521, 97886, 98252,
    # 2170-2179
    98617, 98982, 99347, 99713, 100078, 100443, 100808, 101174, 101539, 101904,
    # 2180-2189
    102269, 102635, 103000, 103365, 103730, 104096, 104461, 104826, 105191, 105557,
    # 2190-2199
    105922, 106287, 106652, 107018, 107383, 107748, 108113, 108479, 108844, 109209,
    # 2200
    109574
]

_MonthLength = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_MonthLeapLength = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_MonthOffset = [0, 31, 59, 90, 120, 151,  # Jan - Jun
                181, 212, 243, 273, 304, 334,  # Jun - Dec
                365]
_MonthLeapOffset = [0, 31, 60, 91, 121, 152,  # Jan - Jun
                    182, 213, 244, 274, 305, 335,  # Jun - Dec
                    366]
