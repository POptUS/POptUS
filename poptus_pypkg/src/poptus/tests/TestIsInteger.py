import unittest

import numpy as np

from poptus.tests._constants import (
    GOOD_INTS, NOT_INT
)
from poptus._variable_checks import is_integer


class TestIsInteger(unittest.TestCase):

    def testFunction(self):
        for good in GOOD_INTS:
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
            bad = str(good)
            self.assertFalse(is_integer(bad))
            bad = [good]
            self.assertFalse(is_integer(bad))
            bad = {good}
            self.assertFalse(is_integer(bad))
            bad = np.array(good)
            self.assertFalse(is_integer(bad))
            bad = np.array([good])
            self.assertFalse(is_integer(bad))

            self.assertTrue(is_integer((good)))
            self.assertFalse(is_integer((good,)))

        for bad in NOT_INT:
            self.assertFalse(is_integer(bad))
