# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

from PyFin.DateUtilities import Date
from PyFin.DateUtilities import Calendar
from PyFin.DateUtilities import Period
from PyFin.DateUtilities import Schedule
from PyFin.Enums import BizDayConventions
from PyFin.Enums import DateGeneration
from PyFin.Enums import TimeUnits
from PyFin.DateUtilities import check_date
from PyFin.DateUtilities import check_period


def isBizDay(holidayCenter, ref):
    cal = Calendar(holidayCenter)
    ref = check_date(ref)
    return cal.isBizDay(ref)


def datesList(fromDate, toDate):
    fromDate = check_date(fromDate)
    toDate = check_date(toDate)
    return [Date.fromExcelSerialNumber(serial).toDateTime() for serial in
            range(fromDate.serialNumber, toDate.serialNumber + 1)]


def bizDatesList(holidayCenter, fromDate, toDate):
    cal = Calendar(holidayCenter)
    fromDate = check_date(fromDate)
    toDate = check_date(toDate)
    return [d.toDateTime() for d in cal.bizDatesList(fromDate, toDate)]


def holDatesList(holidayCenter, fromDate, toDate, includeWeekend=True):
    cal = Calendar(holidayCenter)
    fromDate = check_date(fromDate)
    toDate = check_date(toDate)
    return [d.toDateTime() for d in cal.holDatesList(fromDate, toDate, includeWeekend)]


def advanceDate(referenceDate, period):
    d = check_date(referenceDate) + period
    return d.toDateTime()


def adjustDateByCalendar(holidayCenter, referenceDate, convention=BizDayConventions.Following):
    cal = Calendar(holidayCenter)
    refer = check_date(referenceDate)
    return cal.adjustDate(refer, convention).toDateTime()


def advanceDateByCalendar(holidayCenter, referenceDate, period, convention=BizDayConventions.Following):
    cal = Calendar(holidayCenter)
    refer = check_date(referenceDate)
    period = check_period(period)
    return cal.advanceDate(refer, period, convention).toDateTime()


def nthWeekDay(nth, dayOfWeek, month, year):
    date = Date.nthWeekday(nth, dayOfWeek, month, year)
    return date.toDateTime()


def makeSchedule(firstDate,
                 endDate,
                 tenor,
                 calendar='NullCalendar',
                 dateRule=BizDayConventions.Following,
                 dateGenerationRule=DateGeneration.Forward):

    cal = Calendar(calendar)
    firstDate = check_date(firstDate)
    endDate = check_date(endDate)
    tenor = check_period(tenor)

    if tenor.units() == TimeUnits.BDays:
        schedule = []
        if dateGenerationRule == DateGeneration.Forward:
            d = cal.adjustDate(firstDate, dateRule)
            while d <= endDate:
                schedule.append(d)
                d = cal.advanceDate(d, tenor, dateRule)
        elif dateGenerationRule == DateGeneration.Backward:
            d = cal.adjustDate(endDate, dateRule)
            while d >= firstDate:
                schedule.append(d)
                d = cal.advanceDate(d, -tenor, dateRule)
            schedule = sorted(schedule)
    else:
        schedule = Schedule(firstDate, endDate, tenor, cal, convention=dateRule, dateGenerationRule=dateGenerationRule)
    return [d.toDateTime() for d in schedule]
