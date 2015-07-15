# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

import unittest
from finpy.DateUtilities import Date
from finpy.Env import Settings


class TestSettings(unittest.TestCase):

    def testEvaluationDate(self):
        today = Date.todaysDate()
        self.assertEqual(Settings.evaluationDate, today, "Initial evaluation Date should be \n"
                                                         "expected: {0}\n"
                                                         "returned: {1}".format(today, Settings.evaluationDate))

        referenceDate = Date(2015, 1, 1)
        Settings.evaluationDate = referenceDate
        self.assertEqual(Settings.evaluationDate, referenceDate, "Evaluation Date should be \n"
                                                                 "expected: {0}\n"
                                                                 "returned: {1}".format(referenceDate, Settings.evaluationDate))
