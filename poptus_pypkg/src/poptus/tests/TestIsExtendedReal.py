import warnings
import unittest

import numpy as np

from poptus.tests._constants import (
    EXTENDED_REALS, NOT_EXTENDED_REAL
)
from poptus._variable_checks import is_extended_real


class TestIsExtendedReal(unittest.TestCase):

    def testFunction(self):
        for bad in NOT_EXTENDED_REAL + [-1, 0, 1]:
            self.assertFalse(is_extended_real(bad))

        for good in EXTENDED_REALS:
            self.assertTrue(isinstance(good, np.float64))
            self.assertTrue(is_extended_real(good))
            self.assertTrue(is_extended_real(float(good)))
            self.assertTrue(is_extended_real(-good))
            self.assertTrue(is_extended_real(float(-good)))

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "overflow encountered in cast")

                for cast in [np.float16, np.float32]:
                    good_cast = cast(good)
                    self.assertTrue(is_extended_real(good_cast))

                    good_cast = cast(-good)
                    self.assertTrue(is_extended_real(good_cast))

            # Dress up good values in unacceptable ways
            self.assertTrue(is_extended_real((good)))
            bad_types = (
                str(good), [good], {good}, (good,), np.array(good), np.array([good])
            )
            for bad in bad_types:
                self.assertFalse(is_extended_real(bad))
            for bad in (good + 1j, good + 0.0 * 1j):
                self.assertTrue(isinstance(bad, np.complex128))
                self.assertFalse(is_extended_real(bad))
                self.assertFalse(is_extended_real(complex(bad)))

        for good in np.linspace(-1234.567, 9876.543, 10_000):
            self.assertTrue(isinstance(good, np.float64))
            self.assertTrue(is_extended_real(good))
            self.assertTrue(is_extended_real(float(good)))
            self.assertTrue(is_extended_real(np.float32(good)))
            self.assertTrue(is_extended_real(np.float16(good)))
