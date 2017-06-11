# -*- coding: utf-8 -*-
u"""
Created on 2017-6-11

@author: cheng.li
"""

import unittest
from PyFin.Enums.Frequencies import Frequency
from PyFin.Enums.Compoundings import Compounding
from PyFin.CashFlows.InterestRate import InterestRate
from PyFin.DateUtilities.Date import Date
from PyFin.DateUtilities.DayCounter import DayCounter


class InterestRateData(object):
    def __init__(self, r, comp, freq, t, comp2, freq2, expected, precision):
        self.r = r
        self.comp = comp
        self.freq = freq
        self.t = t
        self.comp2 = comp2
        self.freq2 = freq2
        self.expected = expected
        self.precision = precision


class TestInterestRate(unittest.TestCase):
    def setUp(self):
        self.cases = [
            # data from "Option Pricing Formulas", Haug, pag .181 - 182
            # Rate, Compounding, Frequency, Time, Compounding2, Frequency2, Rate2, precision
            InterestRateData(0.0800, Compounding.Compounded, Frequency.Quarterly, 1.00, Compounding.Continuous,
                             Frequency.Annual, 0.0792, 4),
            InterestRateData(0.1200, Compounding.Continuous, Frequency.Annual, 1.00, Compounding.Compounded,
                             Frequency.Annual, 0.1275, 4),
            InterestRateData(0.0800, Compounding.Compounded, Frequency.Quarterly, 1.00, Compounding.Compounded,
                             Frequency.Annual, 0.0824, 4),
            InterestRateData(0.0700, Compounding.Compounded, Frequency.Quarterly, 1.00, Compounding.Compounded,
                             Frequency.Semiannual, 0.0706, 4),
            # undocumented, but reasonable:)
            InterestRateData(0.0100, Compounding.Compounded, Frequency.Annual, 1.00, Compounding.Simple,
                             Frequency.Annual, 0.0100, 4),
            InterestRateData(0.0200, Compounding.Simple, Frequency.Annual, 1.00, Compounding.Compounded,
                             Frequency.Annual, 0.0200, 4),
            InterestRateData(0.0300, Compounding.Compounded, Frequency.Semiannual, 0.50, Compounding.Simple,
                             Frequency.Annual, 0.0300, 4),
            InterestRateData(0.0400, Compounding.Simple, Frequency.Annual, 0.50, Compounding.Compounded,
                             Frequency.Semiannual, 0.0400, 4),
            InterestRateData(0.0500, Compounding.Compounded, Frequency.EveryFourthMonth, 1.0 / 3, Compounding.Simple,
                             Frequency.Annual, 0.0500, 4),
            InterestRateData(0.0600, Compounding.Simple, Frequency.Annual, 1.0 / 3, Compounding.Compounded,
                             Frequency.EveryFourthMonth, 0.0600, 4),
            InterestRateData(0.0500, Compounding.Compounded, Frequency.Quarterly, 0.25, Compounding.Simple,
                             Frequency.Annual, 0.0500, 4),
            InterestRateData(0.0600, Compounding.Simple, Frequency.Annual, 0.25, Compounding.Compounded,
                             Frequency.Quarterly, 0.0600, 4),
            InterestRateData(0.0700, Compounding.Compounded, Frequency.Bimonthly, 1.0 / 6, Compounding.Simple,
                             Frequency.Annual, 0.0700, 4),
            InterestRateData(0.0800, Compounding.Simple, Frequency.Annual, 1.0 / 6, Compounding.Compounded,
                             Frequency.Bimonthly, 0.0800, 4),
            InterestRateData(0.0900, Compounding.Compounded, Frequency.Monthly, 1.0 / 12, Compounding.Simple,
                             Frequency.Annual, 0.0900, 4),
            InterestRateData(0.1000, Compounding.Simple, Frequency.Annual, 1.0 / 12, Compounding.Compounded,
                             Frequency.Monthly, 0.1000, 4),

            InterestRateData(0.0300, Compounding.SimpleThenCompounded, Frequency.Semiannual, 0.25, Compounding.Simple,
                             Frequency.Annual, 0.0300, 4),
            InterestRateData(0.0300, Compounding.SimpleThenCompounded, Frequency.Semiannual, 0.25, Compounding.Simple,
                             Frequency.Semiannual, 0.0300, 4),
            InterestRateData(0.0300, Compounding.SimpleThenCompounded, Frequency.Semiannual, 0.25, Compounding.Simple,
                             Frequency.Quarterly, 0.0300, 4),
            InterestRateData(0.0300, Compounding.SimpleThenCompounded, Frequency.Semiannual, 0.50, Compounding.Simple,
                             Frequency.Annual, 0.0300, 4),
            InterestRateData(0.0300, Compounding.SimpleThenCompounded, Frequency.Semiannual, 0.50, Compounding.Simple,
                             Frequency.Semiannual, 0.0300, 4),
            InterestRateData(0.0300, Compounding.SimpleThenCompounded, Frequency.Semiannual, 0.75,
                             Compounding.Compounded, Frequency.Semiannual, 0.0300, 4),

            InterestRateData(0.0400, Compounding.Simple, Frequency.Semiannual, 0.25, Compounding.SimpleThenCompounded,
                             Frequency.Quarterly, 0.0400, 4),
            InterestRateData(0.0400, Compounding.Simple, Frequency.Semiannual, 0.25, Compounding.SimpleThenCompounded,
                             Frequency.Semiannual, 0.0400, 4),
            InterestRateData(0.0400, Compounding.Simple, Frequency.Semiannual, 0.25, Compounding.SimpleThenCompounded,
                             Frequency.Annual, 0.0400, 4),

            InterestRateData(0.0400, Compounding.Compounded, Frequency.Quarterly, 0.50,
                             Compounding.SimpleThenCompounded, Frequency.Quarterly, 0.0400, 4),
            InterestRateData(0.0400, Compounding.Simple, Frequency.Semiannual, 0.50, Compounding.SimpleThenCompounded,
                             Frequency.Semiannual, 0.0400, 4),
            InterestRateData(0.0400, Compounding.Simple, Frequency.Semiannual, 0.50, Compounding.SimpleThenCompounded,
                             Frequency.Annual, 0.0400, 4),

            InterestRateData(0.0400, Compounding.Compounded, Frequency.Quarterly, 0.75,
                             Compounding.SimpleThenCompounded, Frequency.Quarterly, 0.0400, 4),
            InterestRateData(0.0400, Compounding.Compounded, Frequency.Semiannual, 0.75,
                             Compounding.SimpleThenCompounded, Frequency.Semiannual, 0.0400, 4),
            InterestRateData(0.0400, Compounding.Simple, Frequency.Semiannual, 0.75, Compounding.SimpleThenCompounded,
                             Frequency.Annual, 0.0400, 4)
        ]

    def testConversion(self):

        d1 = Date.todaysDate()

        for case in self.cases:
            ir = InterestRate(case.r, DayCounter('Actual/360'), case.comp, case.freq)
            d2 = d1 + int(360 * case.t + 0.5)

            compoundf = ir.compoundFactor(d1, d2)
            disc = ir.discountFactor(d1, d2)

            self.assertAlmostEqual(compoundf, 1.0 / disc)

            ir2 = ir.equivalentRate(ir.dayCounter_,
                                    ir.comp_,
                                    ir.freq_,
                                    d1, d2)

            self.assertAlmostEqual(ir2.r_, ir.r_)
            self.assertEqual(ir.freq_, ir2.freq_)
            self.assertEqual(ir.comp_, ir2.comp_)

            ir3 = ir.equivalentRate(ir.dayCounter_,
                                    case.comp2, case.freq2,
                                    d1, d2)
            expectedIR = InterestRate(case.expected, ir.dayCounter_,
                                      case.comp2, case.freq2)
            self.assertAlmostEqual(ir3.r_, expectedIR.r_, case.precision)

            r3 = ir.equivalentRate(ir.dayCounter_,
                                   case.comp2, case.freq2,
                                   d1, d2)
            self.assertAlmostEqual(r3.r_, case.expected, case.precision)


if __name__ == '__main__':
    unittest.main()
