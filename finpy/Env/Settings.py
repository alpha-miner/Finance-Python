# -*- coding: utf-8 -*-
u"""
Created on 2015-8-14

@author: cheng.li
"""

from finpy.Patterns.ClassProperty import ClassPropertyMetaClass
from finpy.Patterns.ClassProperty import classproperty
from finpy.DateUtilities import Date


class Settings(object):
    __metaclass__ = ClassPropertyMetaClass
    _evaluationDate = None

    @classproperty
    def evaluationDate(cls):
        if cls._evaluationDate is None:
            return Date.todaysDate()
        return cls._evaluationDate

    @evaluationDate.setter
    def evaluationDate(cls, value):
        if not isinstance(value, Date):
            raise ValueError("{0} is not a valid finpy date object".format(value))
        cls._evaluationDate = value

    @classmethod
    def resetEvaluationDate(cls):
        cls._evaluationDate = None

    @classmethod
    def anchorEvaluationDate(cls):
        if cls._evaluationDate is None:
            cls._evaluationDate = Date.todaysDate()