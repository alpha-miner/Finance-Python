# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

from PyFin.Patterns.Singleton import Singleton


class MathConstantsFactory(Singleton):
    def __init__(self):
        self._dbl_min = 2.2250738585072014e-308
        self._ql_epsilon = 2.2250738585072014e-308
        self._m_sqrt2 = 1.41421356237309504880
        self._m_sqrt_2 = 0.7071067811865475244008443621048490392848359376887
        self._m_sqrtpi = 1.77245385090551602792981
        self._m_1_sqrtpi = 0.564189583547756286948
        self._m_pi = 3.14159265358979323846

    @property
    def DBL_MIN(self):
        return self._dbl_min

    @property
    def QL_EPSILON(self):
        return self._ql_epsilon

    @property
    def M_SQRT2(self):
        return self._m_sqrt2

    @property
    def M_SQRT_2(self):
        return self._m_sqrt_2

    @property
    def M_SQRTPI(self):
        return self._m_sqrtpi

    @property
    def M_1_SQRTPI(self):
        return self._m_1_sqrtpi

    @property
    def M_PI(self):
        return self._m_pi


MathConstants = MathConstantsFactory()
