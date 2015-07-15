# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import unittest
from finpy.DateUtilities import Date


class TestDate(unittest.TestCase):

    def testConsistency(self):

        minDate = Date.minDate().serialNumber + 1
        maxDate = Date.maxDate().serialNumber

        dyold = Date.fromExcelSerialNumber(minDate - 1).dayOfYear()
        dold = Date.fromExcelSerialNumber(minDate - 1).dayOfMonth()
        mold = Date.fromExcelSerialNumber(minDate - 1).month()
        yold = Date.fromExcelSerialNumber(minDate - 1).year()
        wdold = Date.fromExcelSerialNumber(minDate - 1).weekday()

        for i in range(minDate, maxDate+1):
            t = Date.fromExcelSerialNumber(i)
            serial = t.serialNumber
            self.assertEqual(serial, i, "inconsistent serial number:\n"
                                        "   original:      {0:d}\n"
                                        "   serial number: {1:d}".format(i, serial))

            dy = t.dayOfYear()
            d = t.dayOfMonth()
            m = t.month()
            y = t.year()
            wd = t.weekday()

            flag = (dy == dyold+1) or \
                   (dy == 1 and dyold == 365 and not Date.isLeap(yold)) or \
                   (dy == 1 and dyold == 366 and Date.isLeap(yold))

            self.assertTrue(flag, "wrong day of year increment: \n"
                                  "    date: {0}\n"
                                  "    day of year: {1:d}\n"
                                  "    previous:    {2:d}".format(t, dy, dyold))

            dyold = dy

            flag = (d == dold+1 and m == mold and y == yold) or \
                   (d == 1 and m == mold+1 and y == yold) or \
                   (d == 1 and m == 1 and y == yold+1)

            self.assertTrue(flag, "wrong day,month,year increment: \n"
                                  "    date: {0}\n"
                                  "    year,month,day: {1:d}, {2:d}, {3:d}\n"
                                  "    previous:       {4:d}, {5:d}, {6:d}".format(t, y, m, d, yold, mold, dold))
            dold = d
            mold = m
            yold = y

            self.assertTrue(d >= 1, "invalid day of month: \n"
                                    "    date:  {0}\n"
                                    "    day: {1:d}".format(t, d))

            flag = (m == 1 and d <= 31) or \
                   (m == 2 and d <= 28) or \
                   (m == 2 and d == 29 and Date.isLeap(y)) or \
                   (m == 3 and d <= 31) or \
                   (m == 4 and d <= 30) or \
                   (m == 5 and d <= 31) or \
                   (m == 6 and d <= 30) or \
                   (m == 7 and d <= 31) or \
                   (m == 8 and d <= 31) or \
                   (m == 9 and d <= 30) or \
                   (m == 10 and d <= 31) or \
                   (m == 11 and d <= 30) or \
                   (m == 12 and d <= 31)

            self.assertTrue(flag, "invalid day of month: \n"
                                  "    date:  {0}\n"
                                  "    day: {1:d}".format(t, d))

            flag = (wd == (wdold + 1)) or (wd == 1 or wdold == 7)

            self.assertTrue(flag, "invalid weekday: \n"
                                  "    date:  {0}\n"
                                  "    weekday:  {1:d}\n"
                                  "    previous: {2:d}".format(t, wd, wdold))
            wdold = wd

            s = Date(y, m, d)
            serial = s.serialNumber

            self.assertTrue(serial == i, "inconsistent serial number:\n"
                                         "    date:          {0}\n"
                                         "    serial number: {1:d}\n"
                                         "    cloned date:   {2}\n"
                                         "    serial number: {3:d}".format(t, i, s, serial))

    def testIsoDate(self):
        input_date = "2006-01-15"
        d = Date.parseISO(input_date)
        flag = d.dayOfMonth() == 15 and \
               d.month() == 1 and \
               d.year() == 2006

        self.assertTrue(flag, "Iso date failed\n"
                              " input date:    {0}\n"
                              " day of month:  {1:d}\n"
                              " month:         {2:d}\n"
                              " year:          {3:d}".format(input_date, d.dayOfMonth(), d.month(),  d.year()))

    def testParseDates(self):

        input_date = "2006-01-15"
        d = Date.strptime(input_date, "%Y-%m-%d")
        flag = d == Date(2006, 1, 15)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))

        input_date = "12/02/2012"
        d = Date.strptime(input_date, "%m/%d/%Y")
        flag = d == Date(2012, 12, 2)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))

        d = Date.strptime(input_date, "%d/%m/%Y")
        flag = d == Date(2012, 2, 12)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))

        input_date = "20011002"
        d = Date.strptime(input_date, "%Y%m%d")
        flag = d == Date(2001, 10, 2)

        self.assertTrue(flag, "date parsing failed\n"
                              " input date:    {0:s}\n"
                              " parsed:        {1}".format(input_date, d))