# -*- coding: utf-8 -*-
u"""
Created on 2017-6-8

@author: cheng.li
"""

from PyFin.Env.Settings import Settings
from PyFin.Math.udfs import sign
from PyFin.Utilities.Asserts import pyFinAssert


class IrrFinder(object):

    def __init__(self,
                 leg,
                 npv,
                 dayCounter,
                 comp,
                 freq,
                 includeSettlementDateFlows,
                 settlementDate=None,
                 npvDate=None):
        self._leg = leg
        self._npv = npv
        self._dayCounter = dayCounter
        self._compounding = comp
        self._frequency = freq
        self._includeSettlementDateFlows = includeSettlementDateFlows

        if settlementDate:
            self._settlementDate = settlementDate
        else:
            self._settlementDate = Settings.evaluationDate

        if npvDate:
            self._npvDate = npvDate
        else:
            self._npvDate = self._settlementDate

        self._checkSign()

    def _checkSign(self):
        last_sign = sign(-self._npv)
        sign_changes = 0

        for cf in self._leg:
            if (not cf.hasOccurred(self._settlementDate, self._includeSettlementDateFlows)) \
                    and (not cf.tradingExCoupon(self._settlementDate)):
                this_sign = sign(cf.amount())
                if last_sign * this_sign < 0.:
                    sign_changes += 1
                    break

                if this_sign != 0:
                    last_sign = this_sign

        pyFinAssert(sign_changes == 0,
                    ValueError,
                    'given cash flows cannot result in the given market due to sign change')


class CashFlows(object):

    @staticmethod
    def startDate(leg):
        return



