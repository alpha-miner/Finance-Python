# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

from PyFin.DateUtilities import Date
from PyFin.DateUtilities import Calendar
from PyFin.Enums import BizDayConventions
from PyFin.Utilities import check_date


def isBizDay(holidayCenter, ref):
    cal = Calendar(holidayCenter)
    ref = check_date(ref)
    return cal.isBizDay(ref)


def datesList(fromDate, toDate):
    fromDate = check_date(fromDate)
    toDate = check_date(toDate)
    assert fromDate <= toDate, "from date ({0} must be earlier than to date {1}".format(fromDate, toDate)
    return [Date.fromExcelSerialNumber(serial).toDateTime() for serial in
            range(fromDate.serialNumber, toDate.serialNumber + 1)]


def bizDatesList(holidayCenter, fromDate, toDate):
    cal = Calendar(holidayCenter)
    fromDate = check_date(fromDate)
    toDate = check_date(toDate)
    assert fromDate <= toDate, "from date ({0} must be earlier than to date {1}".format(fromDate, toDate)
    return [d.toDateTime() for d in cal.bizDatesList(fromDate, toDate)]


def holDatesList(holidayCenter, fromDate, toDate, includeWeekend=True):
    cal = Calendar(holidayCenter)
    fromDate = check_date(fromDate)
    toDate = check_date(toDate)
    assert fromDate <= toDate, "from date ({0} must be earlier than to date {1}".format(fromDate, toDate)
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
    return cal.advanceDate(refer, period, convention).toDateTime()


def nthWeekDay(nth, dayOfWeek, month, year):
    date = Date.nthWeekday(nth, dayOfWeek, month, year)
    return date.toDateTime()

