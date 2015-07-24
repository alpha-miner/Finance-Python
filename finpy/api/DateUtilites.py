# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

from finpy.DateUtilities import Date
from finpy.DateUtilities import Calendar
from finpy.Enums import BizDayConventions


def datesList(fromDate, toDate):

    fromDate = Date.parseISO(fromDate)
    toDate = Date.parseISO(toDate)
    assert fromDate <= toDate, "from date ({0:s} must be earlier than to date {1:s}".format(fromDate, toDate)
    return [Date.fromExcelSerialNumber(serial).toDateTime() for serial in range(fromDate.serialNumber, toDate.serialNumber+1)]


def bizDatesList(holidayCenter, fromDate, toDate):
    cal = Calendar(holidayCenter)
    fromDate = Date.parseISO(fromDate)
    toDate = Date.parseISO(toDate)
    return [d.toDateTime() for d in cal.bizDatesList(fromDate, toDate)]


def holDatesList(holidayCenter, fromDate, toDate, includeWeekend=True):
    cal = Calendar(holidayCenter)
    fromDate = Date.parseISO(fromDate)
    toDate = Date.parseISO(toDate)
    return [d.toDateTime() for d in cal.holDatesList(fromDate, toDate, includeWeekend)]


def advanceDate(referenceDate, period):
    d = Date.parseISO(referenceDate) + period
    return d.toDateTime()


def adjustDateByCalendar(holidayCenter, referenceDate, convention=BizDayConventions.Following):
    cal = Calendar(holidayCenter)
    refer = Date.parseISO(referenceDate)
    return cal.adjustDate(refer, convention).toDateTime()


def advanceDateByCalendar(holidayCenter, referenceDate, period, convention=BizDayConventions.Following):
    cal = Calendar(holidayCenter)
    refer = Date.parseISO(referenceDate)
    return cal.advanceDate(refer, period, convention).toDateTime()