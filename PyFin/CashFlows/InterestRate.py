# -*- coding: utf-8 -*-
u"""
Created on 2017-6-11

@author: cheng.li
"""

from math import exp
from math import log
from PyFin.Enums.Compoundings import Compounding
from PyFin.Enums.Frequencies import Frequency
from PyFin.Utilities.Asserts import pyFinAssert


class InterestRate(object):

    def __init__(self, r, dayCounter, comp, freq):
        self.r_ = r
        self.dayCounter_ = dayCounter
        self.comp_ = comp
        self.freqMakesSense_ = False
        self.freq_ = freq
        if self.comp_ == Compounding.Compounded \
                or self.comp_ == Compounding.SimpleThenCompounded \
                or self.comp_ == Compounding.CompoundedThenSimple:
            self.freqMakesSense_ = True
            pyFinAssert(freq != Frequency.Once and freq != Frequency.OtherFrequency,
                        ValueError,
                        "frequency not allowed for this interest rate")
            self.freq_ = float(freq)

    def compoundFactorImpl(self, t):
        if self.comp_ == Compounding.Simple:
            return 1. + self.r_ * t
        elif self.comp_ == Compounding.Compounded:
            return (1. + self.r_ / self.freq_) ** (self.freq_ * t)
        elif self.comp_ == Compounding.Continuous:
            return exp(self.r_ * t)
        elif self.comp_ == Compounding.SimpleThenCompounded:
            if t <= 1.0 / self.freq_:
                return 1.0 + self.r_ * t
            else:
                return (1.0 + self.r_ / self.freq_) ** (self.freq_ * t)
        elif self.comp_ == Compounding.CompoundedThenSimple:
            if t > 1.0 / self.freq_:
                return 1.0 + self.r_ * t
            else:
                return (1.0 + self.r_ / self.freq_) ** (self.freq_ * t)
        else:
            raise ValueError('unknown compounding convention')

    def discountFactorImpl(self, t):
        return 1. / self.compoundFactorImpl(t)

    def compoundFactor(self, d1, d2, refStart=None, refEnd=None):
        t = self.dayCounter_.yearFraction(d1, d2, refStart, refEnd)
        return self.compoundFactorImpl(t)

    def discountFactor(self, d1, d2, refStart=None, refEnd=None):
        return 1. / self.compoundFactor(d1, d2, refStart, refEnd)

    @staticmethod
    def impliedRate(compound, resultDC, comp, freq, t):
        if compound == 1.0:
            r = 0.0
        else:
            if comp == Compounding.Simple:
                r = (compound - 1.0) / t
            elif comp == Compounding.Compounded:
                r = (compound ** (1.0 / (freq * t)) - 1.0) * freq
            elif comp == Compounding.Continuous:
                r = log(compound) / t
            elif comp == Compounding.SimpleThenCompounded:
                if t <= 1.0 / freq:
                    r = (compound - 1.0) / t
                else:
                    r = (compound ** (1.0 / (freq * t)) - 1.0) * freq
            elif comp == Compounding.CompoundedThenSimple:
                if t > 1.0 / freq:
                    r = (compound - 1.0) / t
                else:
                    r = (compound ** (1.0 / (freq * t)) - 1.0) * freq
            else:
                raise ValueError('unknown compounding convention')

        return InterestRate(r, resultDC, comp, freq)

    def equivalentRate(self, resultDC, comp, freq, d1, d2, refStart=None, refEnd=None):
        t1 = self.dayCounter_.yearFraction(d1, d2, refStart, refEnd)
        t2 = resultDC.yearFraction(d1, d2, refStart, refEnd)
        return self.impliedRate(self.compoundFactorImpl(t1), resultDC, comp, freq, t2)



