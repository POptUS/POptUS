"""
Automatic unittest of the AbstractLogger class
"""

import unittest

import poptus


class TestAbstractLogger(unittest.TestCase):
    def testAbstract(self):
        # Confirm that class is abstract and cannot be instantiated
        with self.assertRaises(TypeError):
            poptus.AbstractLogger(poptus.LOG_LEVEL_DEFAULT)
        self.assertTrue(False)
