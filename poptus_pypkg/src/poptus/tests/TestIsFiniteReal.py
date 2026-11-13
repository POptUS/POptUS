import warnings
import unittest

import numpy as np

from poptus.tests._constants import (
    FINITE_REALS, NOT_FINITE_REAL
)
from poptus._variable_checks import is_finite_real


class TestIsFiniteReal(unittest.TestCase):

    def testFunction(self):
        for good in FINITE_REALS:
            self.assertTrue(isinstance(good, np.float64))
            self.assertTrue(is_finite_real(good))
            self.assertTrue(is_finite_real(float(good)))
            self.assertTrue(is_finite_real(-good))
            self.assertTrue(is_finite_real(float(-good)))

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "overflow encountered in cast")

                for cast in [np.float16, np.float32]:
                    good_cast = cast(good)
                    if good_cast != np.inf:
                        self.assertTrue(is_finite_real(good_cast))
                    else:
                        self.assertFalse(is_finite_real(good_cast))

                    good_cast = cast(-good)
                    if good_cast != -np.inf:
                        self.assertTrue(is_finite_real(good_cast))
                    else:
                        self.assertFalse(is_finite_real(good_cast))

            # Dress up good values in unacceptable ways
            bad = str(good)
            self.assertFalse(is_finite_real(bad))
            bad = good + 1j
            self.assertTrue(isinstance(bad, np.complex128))
            self.assertFalse(is_finite_real(bad))
            self.assertFalse(is_finite_real(complex(bad)))
            bad = good + 0.0 * 1j
            self.assertTrue(isinstance(bad, np.complex128))
            self.assertFalse(is_finite_real(bad))
            self.assertFalse(is_finite_real(complex(bad)))
            bad = [good]
            self.assertFalse(is_finite_real(bad))
            bad = {good}
            self.assertFalse(is_finite_real(bad))
            bad = np.array(good)
            self.assertFalse(is_finite_real(bad))
            bad = np.array([good])
            self.assertFalse(is_finite_real(bad))

            self.assertTrue(is_finite_real((good)))
            self.assertFalse(is_finite_real((good,)))

        for good in np.linspace(-1234.567, 9876.543, 10_000):
            self.assertTrue(isinstance(good, np.float64))
            self.assertTrue(is_finite_real(good))
            self.assertTrue(is_finite_real(float(good)))
            self.assertTrue(is_finite_real(np.float32(good)))

        for bad in NOT_FINITE_REAL:
            self.assertFalse(is_finite_real(bad))
