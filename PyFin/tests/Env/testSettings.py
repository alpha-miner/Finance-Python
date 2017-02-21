# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

import unittest
from PyFin.DateUtilities import Date
from PyFin.Env import Settings


class TestSettings(unittest.TestCase):
    def testEvaluationDate(self):
        referenceDate = Date(2015, 1, 1)
        Settings.evaluationDate = referenceDate
        self.assertEqual(Settings.evaluationDate, referenceDate, "Evaluation Date should be \n"
                                                                 "expected:   {0}\n"
                                                                 "calculated: {1}".format(referenceDate,
                                                                                          Settings.evaluationDate))

        # check wrong input
        with self.assertRaises(ValueError):
            Settings.evaluationDate = 2
