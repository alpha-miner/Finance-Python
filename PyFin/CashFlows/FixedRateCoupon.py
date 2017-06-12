# -*- coding: utf-8 -*-
u"""
Created on 2017-6-12

@author: cheng.li
"""

from PyFin.CashFlows.CashFlow import Coupon
from PyFin.CashFlows.InterestRate import InterestRate
from PyFin.Enums.Compoundings import Compounding
from PyFin.Enums.Frequencies import Frequency


class FixedRateCoupon(Coupon):

    def __init__(self,
                 paymentDate,
                 norminal,
                 rate,
                 dayCounter,
                 accrualStartDate,
                 accrualEndDate,
                 refPeriodStart=None,
                 refPeriodEnd=None,
                 exCouponDate=None):
        super(FixedRateCoupon, self).__init__(paymentDate,
                                              norminal,
                                              accrualStartDate,
                                              accrualEndDate,
                                              refPeriodStart,
                                              refPeriodEnd,
                                              exCouponDate)
        self.rate_ = InterestRate(rate, dayCounter, Compounding.Simple, Frequency.Annual)

    def amount(self):
        return self.norminal_ * (self.rate_.compoundFactor(self.accrualStartDate_,
                                                           self.accrualEndDate_,
                                                           self.refPeriodStart_,
                                                           self.refPeriodEnd_) - 1.0)

    def accruedAmount(self, d):
        if d <= self.accrualStartDate_ or d > self.paymentDate_:
            return 0.
        elif self.tradingExCoupon(d):
            return -self.norminal_ * (self.rate_.compoundFactor(d,
                                                                self.accrualEndDate_,
                                                                self.refPeriodStart_,
                                                                self.refPeriodEnd_) - 1.0)
        else:
            return self.norminal_ * (self.rate_.compoundFactor(self.accrualStartDate_,
                                                               min(d, self.accrualEndDate_),
                                                               self.refPeriodStart_,
                                                               self.refPeriodEnd_) - 1.0)


class FixedRateLeg(object):
    pass