# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

from PyFin.DateUtilities import Date
from PyFin.DateUtilities import Calendar
from PyFin.Enums import BizDayConventions


def isBizDay(holidayCenter, ref):
    cal = Calendar(holidayCenter)
    ref = Date.fromDateTime(ref)
    return cal.isBizDay(ref)


def datesList(fromDate, toDate):
    fromDate = Date.fromDateTime(fromDate)
    toDate = Date.fromDateTime(toDate)
    assert fromDate <= toDate, "from date ({0} must be earlier than to date {1}".format(fromDate, toDate)
    return [Date.fromExcelSerialNumber(serial).toDateTime() for serial in
            range(fromDate.serialNumber, toDate.serialNumber + 1)]


def bizDatesList(holidayCenter, fromDate, toDate):
    cal = Calendar(holidayCenter)
    fromDate = Date.fromDateTime(fromDate)
    toDate = Date.fromDateTime(toDate)
    assert fromDate <= toDate, "from date ({0} must be earlier than to date {1}".format(fromDate, toDate)
    return [d.toDateTime() for d in cal.bizDatesList(fromDate, toDate)]


def holDatesList(holidayCenter, fromDate, toDate, includeWeekend=True):
    cal = Calendar(holidayCenter)
    fromDate = Date.fromDateTime(fromDate)
    toDate = Date.fromDateTime(toDate)
    assert fromDate <= toDate, "from date ({0} must be earlier than to date {1}".format(fromDate, toDate)
    return [d.toDateTime() for d in cal.holDatesList(fromDate, toDate, includeWeekend)]


def advanceDate(referenceDate, period):
    d = Date.fromDateTime(referenceDate) + period
    return d.toDateTime()


def adjustDateByCalendar(holidayCenter, referenceDate, convention=BizDayConventions.Following):
    cal = Calendar(holidayCenter)
    refer = Date.fromDateTime(referenceDate)
    return cal.adjustDate(refer, convention).toDateTime()


def advanceDateByCalendar(holidayCenter, referenceDate, period, convention=BizDayConventions.Following):
    cal = Calendar(holidayCenter)
    refer = Date.fromDateTime(referenceDate)
    return cal.advanceDate(refer, period, convention).toDateTime()

