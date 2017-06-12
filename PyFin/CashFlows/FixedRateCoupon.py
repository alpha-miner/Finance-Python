# -*- coding: utf-8 -*-
u"""
Created on 2017-6-12

@author: cheng.li
"""

from PyFin.CashFlows.CashFlow import Coupon
from PyFin.CashFlows.InterestRate import InterestRate
from PyFin.Enums.Compoundings import Compounding
from PyFin.Enums.Frequencies import Frequency
from PyFin.Enums.BizDayConventions import BizDayConventions


class FixedRateCoupon(Coupon):

    def __init__(self,
                 paymentDate,
                 norminal,
                 interestRate,
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
        self.rate_ = interestRate

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

    def __init__(self, schedule):
        self.schedule_ = schedule
        self.calendar_ = self.schedule_.calendar()
        self.paymentAdjustment_ = BizDayConventions.Following
        self.firstPeriodDC_ = None
        self.notionals_ = None
        self.couponRates_ = None
        self.exCouponPeriod_ = None
        self.exCouponCalendar_ = None
        self.exCouponAdjustment_ = None
        self.exCouponEndOfMonth_ = None

    def withNotionals(self, notionals):
        self.notionals_ = notionals
        return self

    def withCouponRate(self, rate, dc, comp, freq):
        self.couponRates_ = []
        self.couponRates_.append(InterestRate(rate, dc, comp, freq))
        return self

    def withCouponRateByInterestRate(self, ir):
        self.couponRates_ = []
        self.couponRates_.append(ir)
        return self

    def withPaymentAdjustment(self, convention):
        self.paymentAdjustment_ = convention
        return self

    def withFirstPeriodDayCounter(self, dc):
        self.firstPeriodDC_ = dc
        return self

    def withPaymentCalendar(self, cal):
        self.calendar_ = cal
        return self

    def withExCouponPeriod(self, period, cal, convention, endOfMonth):
        self.exCouponPeriod_ = period
        self.exCouponCalendar_ = cal
        self.exCouponAdjustment_ = convention
        self.exCouponEndOfMonth_ = endOfMonth
        return self

    def toLeg(self):
        leg = []
        start = self.schedule_._dates[0]
        end = self.schedule_._dates[1]
        paymentDate = self.calendar_.adjustDate(end, self.paymentAdjustment_)
        rate = self.couponRates_[0]
        nominal = self.notionals_[0]

        exCouponDate = None

        if self.exCouponPeriod_:
            exCouponDate = self.exCouponCalendar_.advanceDate(paymentDate,
                                                              -self.exCouponPeriod_,
                                                              self.exCouponAdjustment_,
                                                              self.exCouponEndOfMonth_)

        if self.schedule_.isRegular(1):
            leg.append(FixedRateCoupon(paymentDate, nominal, rate, start, end, start, end, exCouponDate))
        else:
            ref = self.schedule_.calendar().advanceDate(end,
                                                        -self.schedule_.tenor(),
                                                        self.schedule_._convention,
                                                        self.schedule_.endOfMonth())
            r = InterestRate(rate.r_,
                             self.firstPeriodDC_ if self.firstPeriodDC_ else rate.dayCounter_,
                             rate.comp_,
                             rate.freq_)
            leg.append(FixedRateCoupon(paymentDate,
                                       nominal,
                                       r,
                                       start,
                                       end,
                                       ref,
                                       end,
                                       exCouponDate))

        for i in range(2, self.schedule_.size()-1):
            start = end
            end = self.schedule_._dates[i]
            paymentDate = self.calendar_.adjustDate(end, self.paymentAdjustment_)

            if self.exCouponPeriod_:
                exCouponDate = self.exCouponCalendar_.advanceDate(paymentDate,
                                                                  -self.exCouponPeriod_,
                                                                  self.exCouponAdjustment_,
                                                                  self.exCouponEndOfMonth_)

            if (i - 1) < len(self.couponRates_):
                rate = self.couponRates_[i - 1]
            else:
                rate = self.couponRates_[-1]
            if (i - 1) < len(self.notionals_):
                nominal = self.notionals_[i - 1]
            else:
                nominal = self.notionals_[-1]
            leg.append(FixedRateCoupon(paymentDate,
                                       nominal,
                                       rate,
                                       start,
                                       end,
                                       start,
                                       end,
                                       exCouponDate))

        if self.schedule_.size() > 2:
            # last period might be short or long
            N = self.schedule_.size()
            start = end
            end = self.schedule_._dates[N - 1]
            paymentDate = self.calendar_.adjustDate(end, self.paymentAdjustment_)
            if self.exCouponPeriod_:
                exCouponDate = self.exCouponCalendar_.advanceDate(paymentDate,
                                                                  -self.exCouponPeriod_,
                                                                  self.exCouponAdjustment_,
                                                                  self.exCouponEndOfMonth_)
            if (N - 2) < len(self.couponRates_):
                rate = self.couponRates_[N - 2]
            else:
                rate = self.couponRates_[-1]
            if (N - 2) < len(self.notionals_):
                nominal = self.notionals_[N - 2]
            else:
                nominal = self.notionals_[-1]

            if self.schedule_.isRegular(N - 1):
                leg.append(FixedRateCoupon(paymentDate,
                                           nominal,
                                           rate,
                                           start,
                                           end,
                                           start,
                                           end,
                                           exCouponDate))
            else:
                ref = self.schedule_.calendar().advance(start,
                                                        self.schedule_.tenor(),
                                                        self.schedule_._convention,
                                                        self.schedule_.endOfMonth())
                leg.append(FixedRateCoupon(paymentDate,
                                           nominal,
                                           rate,
                                           start,
                                           end,
                                           start,
                                           ref,
                                           exCouponDate))

        return leg
