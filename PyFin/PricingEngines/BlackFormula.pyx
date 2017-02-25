# -*- coding: utf-8 -*-
u"""
Created on 2017-2-4

@author: cheng.li
"""

cimport cython
from libc.math cimport log
from libc.math cimport exp
from libc.math cimport sqrt
from libc.math cimport fabs
from libc.math cimport fmax
from libc.math cimport fmin
from libc.math cimport atanh
from PyFin.Enums._OptionType cimport OptionType
from libc.stdlib cimport malloc
from libc.stdlib cimport free
from PyFin.Math.Distributions.norm cimport cdf
from PyFin.Math.Distributions.norm cimport pdf
from PyFin.Math.Distributions.norm cimport cdf_derivative

cdef double _M_PI = 3.14159265358979323846
cdef double _M_SQRT_2 = 0.7071067811865475244008443621048490392848359376887
cdef double _M_1_SQRTPI = 0.564189583547756286948
cdef double _QL_EPSILON = 2.2250738585072014e-308

cdef int _checkParameters(double strike, double forward, double displacement) nogil:
    if displacement >= 0 and strike + displacement >= 0 and forward + displacement >= 0:
        return 0
    else:
        return -1

@cython.cdivision(True)
cdef double _bsImpl(int optionType,
                    double strike,
                    double forward,
                    double stdDev,
                    double discount=1.0,
                    double displacement=0.0) nogil:
    cdef double d1
    cdef double d2
    cdef double nd1
    cdef double nd2

    if stdDev == 0.0:
        return fmax((forward - strike) * optionType, 0.0) * discount

    forward += displacement
    strike += displacement

    if strike == 0.0:
        return forward * discount if optionType == OptionType.Call else 0.0

    d1 = log(forward / strike) / stdDev + 0.5 * stdDev
    d2 = d1 - stdDev
    nd1 = cdf(d1 * optionType)
    nd2 = cdf(d2 * optionType)

    return discount * optionType * (forward * nd1 - strike * nd2)

@cython.cdivision(True)
cdef double _bsImplWithDerivative(double*dStdDev,
                                  int optionType,
                                  double strike,
                                  double forward,
                                  double stdDev,
                                  double discount=1.0,
                                  double displacement=0.0) nogil:
    cdef double d1
    cdef double d2
    cdef double nd1
    cdef double nd2

    if stdDev == 0.0:
        return fmax((forward - strike) * optionType, 0.0) * discount

    forward += displacement
    strike += displacement

    if strike == 0.0:
        return forward * discount if optionType == OptionType.Call else 0.0

    d1 = log(forward / strike) / stdDev + 0.5 * stdDev
    d2 = d1 - stdDev
    nd1 = cdf(d1 * optionType)
    nd2 = cdf(d2 * optionType)

    dStdDev[0] = discount * strike * pdf(optionType * d2, 2.0, _M_SQRT_2 * _M_1_SQRTPI)
    return discount * optionType * (forward * nd1 - strike * nd2)

cpdef double blackFormula(int optionType,
                 double strike,
                 double forward,
                 double stdDev,
                 double discount=1.0,
                 double displacement=0.0) nogil:
    cdef int flag = _checkParameters(strike, forward, displacement)
    return _bsImpl(optionType, strike, forward, stdDev, discount, displacement)

cpdef double blackFormula2(int optionType,
                  double strike,
                  double forward,
                  double tte,
                  double vol,
                  double riskFree=0.0,
                  double displacement=0.0):
    cdef double discount
    cdef double stdDev
    cdef int flag = _checkParameters(strike, forward, displacement)

    if tte == 0.0:
        return fmax((forward - strike) * optionType, 0.0)

    discount = exp(-riskFree * tte)
    stdDev = sqrt(tte) * vol
    return _bsImpl(optionType,
                   strike,
                   forward,
                   stdDev,
                   discount,
                   displacement)

@cython.cdivision(True)
cdef double _bsImplStdDevAppr(int optionType, double strike, double forward, double blackPrice, double discount=1.0,
                              double displacement=0.0) nogil:
    cdef double result0
    cdef double moneynessDelta
    cdef double moneynessDelta_2
    cdef double temp
    cdef double moneynessDelta_PI
    cdef double temp2
    cdef double innerTmp
    cdef double innerTmp2
    cdef double result1

    forward += displacement
    strike += displacement

    if strike == forward:
        return blackPrice / discount * sqrt(2.0 * _M_PI) / forward
    else:
        moneynessDelta = optionType * (forward - strike)
        moneynessDelta_2 = moneynessDelta / 2.0
        temp = blackPrice / discount - moneynessDelta_2
        moneynessDelta_PI = moneynessDelta * moneynessDelta / _M_PI
        temp2 = temp * temp - moneynessDelta_PI

        innerTmp = 0.0
        innerTmp2 = 0.0

        if temp2 < innerTmp:
            temp2 = innerTmp2

        temp2 = sqrt(temp2)
        temp += temp2
        temp *= sqrt(2.0 * _M_PI)
        return temp / (forward + strike)

@cython.cdivision(True)
cdef double _bsImplStdDev(int optionType,
                          double strike,
                          double forward,
                          double blackPrice,
                          double discount=1.0,
                          double displacement=0.0,
                          double xAccuracy=1e-5) nogil:
    cdef double stdDev
    cdef double stdDevOld
    cdef double err
    cdef double diff
    cdef int count = 0
    cdef double*dStdDev = <double *> malloc(sizeof(double))

    # using newton step to fine tune the stdDev
    stdDev = _bsImplStdDevAppr(optionType, strike, forward, blackPrice, discount, displacement)

    err = _bsImplWithDerivative(dStdDev, optionType, strike, forward, stdDev, discount, displacement) - blackPrice
    while count <= 100:
        count += 1
        stdDevOld = stdDev
        diff = err / dStdDev[0]
        stdDev -= diff
        err = _bsImplWithDerivative(dStdDev, optionType, strike, forward, stdDev, discount, displacement) - blackPrice

        if fabs(diff) <= xAccuracy:
            break

    free(dStdDev)
    return stdDev

cpdef double blackFormulaImpliedStdDev(int optionType,
                                double strike,
                                double forward,
                                double blackPrice,
                                double discount=1.0,
                                double displacement=0.0,
                                double xAccuracy=1e-5) nogil:
    return _bsImplStdDev(optionType,
                         strike,
                         forward,
                         blackPrice,
                         discount,
                         displacement,
                         xAccuracy)

cpdef double blackFormulaImpliedVol(int optionType,
                             double strike,
                             double forward,
                             double tte,
                             double blackPrice,
                             double riskFree=0.0,
                             double displacement=0.0) nogil:
    cdef double discount = exp(-riskFree * tte)
    stdDev = _bsImplStdDev(optionType,
                           strike,
                           forward,
                           blackPrice,
                           discount,
                           displacement)
    return stdDev / sqrt(tte)

@cython.cdivision(True)
cpdef double bachelierFormula(int optionType,
                              double strike,
                              double forward,
                              double stdDev,
                              double discount=1.0) nogil:
    cdef double d
    d = (forward - strike) * optionType
    if stdDev == 0:
        return discount * fmax(d, 0.0)

    h = d / stdDev
    result = discount * (stdDev * cdf_derivative(h) + d * cdf(h))
    return result

cdef double _A0 = 3.994961687345134e-1
cdef double _A1 = 2.100960795068497e+1
cdef double _A2 = 4.980340217855084e+1
cdef double _A3 = 5.988761102690991e+2
cdef double _A4 = 1.848489695437094e+3
cdef double _A5 = 6.106322407867059e+3
cdef double _A6 = 2.493415285349361e+4
cdef double _A7 = 1.266458051348246e+4

cdef double _B0 = 1.000000000000000e+0
cdef double _B1 = 4.990534153589422e+1
cdef double _B2 = 3.093573936743112e+1
cdef double _B3 = 1.495105008310999e+3
cdef double _B4 = 1.323614537899738e+3
cdef double _B5 = 1.598919697679745e+4
cdef double _B6 = 2.392008891720782e+4
cdef double _B7 = 3.608817108375034e+3
cdef double _B8 = -2.067719486400926e+2
cdef double _B9 = 1.174240599306013e+1

@cython.cdivision(True)
cdef double _hcalculate(double eta) nogil:
    cdef double num
    cdef double den

    num = _A0 + eta * (_A1 + eta * (_A2 + eta * (_A3 + eta
                                                 * (_A4 + eta * (
        _A5 + eta * (_A6 + eta * _A7))))))

    den = _B0 + eta * (_B1 + eta * (_B2 + eta * (_B3 + eta * (_B4 + eta
                                                              * (_B5 + eta * (
        _B6 + eta * (_B7 + eta * (_B8 + eta * _B9))))))))

    return sqrt(eta) * (num / den)

@cython.cdivision(True)
cpdef double bachelierFormulaImpliedVol(int optionType,
                                        double strike,
                                        double forward,
                                        double tte,
                                        double bachelierPrice,
                                        double discount=1.0) nogil:
    cdef double SQRT_QL_EPSILON
    cdef double forwardPremium
    cdef double straddlePremium
    cdef double nu
    cdef double eta
    cdef double heta

    SQRT_QL_EPSILON = sqrt(_QL_EPSILON)

    forwardPremium = bachelierPrice / discount

    if optionType == OptionType.Call:
        straddlePremium = 2.0 * forwardPremium - (forward - strike)
    else:
        straddlePremium = 2.0 * forwardPremium + (forward - strike)

    nu = (forward - strike) / straddlePremium
    nu = fmax(-1.0, fmin(nu, 1.0))
    eta = 1.0 if (fabs(nu) < SQRT_QL_EPSILON) else (nu / atanh(nu))

    heta = _hcalculate(eta)
    return sqrt(_M_PI / (2. * tte)) * straddlePremium * heta
