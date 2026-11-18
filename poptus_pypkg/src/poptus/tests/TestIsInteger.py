import unittest

import numpy as np

from poptus.tests._constants import (
    GOOD_INTEGERS, NOT_INTEGER
)
from poptus._variable_checks import is_integer


class TestIsInteger(unittest.TestCase):

    def testFunction(self):
        for bad in NOT_INTEGER + [-1.0, 0.0, 1.0]:
            self.assertFalse(is_integer(bad))

        for good in GOOD_INTEGERS:
            self.assertTrue(isinstance(good, int))
            self.assertTrue(is_integer(good))

            self.assertTrue(is_integer(np.int64(good)))
            try:
                self.assertTrue(is_integer(np.int32(good)))
            except OverflowError:
                pass
            try:
                self.assertTrue(is_integer(np.int8(good)))
            except OverflowError:
                pass

            if good >= 0:
                self.assertTrue(is_integer(np.uint64(good)))
                try:
                    self.assertTrue(is_integer(np.uint32(good)))
                except OverflowError:
                    pass
                try:
                    self.assertTrue(is_integer(np.uint8(good)))
                except OverflowError:
                    pass

            # Dress up good values in unacceptable ways
            self.assertTrue(is_integer((good)))
            bad_types = (
                str(good), [good], {good}, (good,), np.array(good), np.array([good])
            )
            for bad in bad_types:
                self.assertFalse(is_integer(bad))
