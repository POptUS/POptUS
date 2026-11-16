import copy
import unittest
import warnings

import numpy as np

from poptus.tests._constants import (
    EXTENDED_REALS,
    NOT_NUMPY_ARRAY
)
from poptus._variable_checks import (
    is_extended_real_numpy_vector,
    is_extended_real_numpy_array
)


class TestIsExtendedRealNumpyArray(unittest.TestCase):

    def setUp(self):
        self.__N_TO_TEST = {2, 3, 5, 10}
        self.__NDIMS_TO_TEST = {2, 3, 4}

    def testNotArrays(self):
        # Test only on acceptable dimensions even though these arguments have
        # nothing generally to do with dimensions
        for ndim in self.__NDIMS_TO_TEST:
            for bad in NOT_NUMPY_ARRAY:
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))

            for good_real in EXTENDED_REALS:
                self.assertFalse(is_extended_real_numpy_array(good_real, ndim))
                bad = str(good_real)
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = good_real + 1j
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = good_real + 0.0 * 1j
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = (good_real)
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = (good_real,)
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = [good_real]
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = [[good_real]]
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = {good_real}
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))
                bad = {"bad": good_real}
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))

    def test0dArrays(self):
        # 0D arrays are strange, so check this carefully
        for good_real in EXTENDED_REALS:
            good_0d = np.array(good_real)
            self.assertTrue(isinstance(good_0d, np.ndarray))
            self.assertEqual(good_0d.ndim, 0)
            self.assertTrue(np.isreal(good_0d))
            self.assertFalse(np.isnan(good_0d))
            self.assertEqual(np.squeeze(good_0d), good_real)

            with self.assertRaises(AssertionError):
                self.assertFalse(is_extended_real_numpy_array(good_0d, 0))

    def test1dArrays(self):
        for good_real in EXTENDED_REALS:
            bad = np.array([good_real])
            self.assertEqual(bad.ndim, 1)
            self.assertTrue(is_extended_real_numpy_vector(bad))

            with self.assertRaises(AssertionError):
                self.assertFalse(is_extended_real_numpy_array(bad, 1))

            bad = np.full(5, good_real)
            self.assertEqual(bad.ndim, 1)
            self.assertTrue(is_extended_real_numpy_vector(bad))

            with self.assertRaises(AssertionError):
                self.assertFalse(is_extended_real_numpy_array(bad, 1))

    def testAllArrays(self):
        self.__testArray((1, 1))
        self.__testArray((1, 1, 1))
        self.__testArray((1, 1, 1, 1))

        for N in self.__N_TO_TEST:
            self.__testArray((N, 1))
            self.__testArray((1, N))

            self.__testArray((N, 1, 1))
            self.__testArray((1, N, 1))
            self.__testArray((1, 1, N))
            self.__testArray((N, 2, 1))
            self.__testArray((N, 1, 2))
            self.__testArray((N, 2, 2))

            # Don't check all possible "2D" combinations
            self.__testArray((N, 1, 1, 1))
            self.__testArray((1, N, 1, 1))
            self.__testArray((1, 1, N, 1))
            self.__testArray((1, 1, 1, N))
            self.__testArray((N, 2, 1, 1))
            self.__testArray((N, 1, 2, 1))
            self.__testArray((N, 1, 1, 2))
            self.__testArray((N, 2, 2, 1))
            self.__testArray((N, 2, 1, 2))
            self.__testArray((N, 1, 2, 2))
            self.__testArray((1, N, 2, 2))
            self.__testArray((N, 2, 2, 2))

    def __testArray(self, vec_shape):
        ndim = len(vec_shape)
        self.assertTrue(ndim in self.__NDIMS_TO_TEST)

        for good_real in EXTENDED_REALS:
            good = np.full(vec_shape, good_real)
            self.assertEqual(good.dtype, np.float64)
            self.assertEqual(good.ndim, ndim)
            self.assertTrue(is_extended_real_numpy_array(good, ndim))
            for bad in self.__NDIMS_TO_TEST.difference({ndim}):
                self.assertFalse(is_extended_real_numpy_array(good, bad))

            # Confirm that the helpers accepts different float types
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "overflow encountered in cast")

                for floating in [np.float16, np.float32]:
                    good = np.full(vec_shape, good_real, floating)
                    self.assertTrue(is_extended_real_numpy_array(good, ndim))

                    good = np.full(vec_shape, -good_real, floating)
                    self.assertTrue(is_extended_real_numpy_array(good, ndim))

            self.assertFalse(is_extended_real_numpy_array(good.tolist(), ndim))
            self.assertFalse(is_extended_real_numpy_array(tuple(good.tolist()), ndim))

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "invalid value encountered in cast")

                bad = good.astype(int)
                self.assertEqual(bad.ndim, ndim)
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))

            bad = good.astype(str)
            self.assertEqual(bad.ndim, ndim)
            self.assertFalse(is_extended_real_numpy_array(bad, ndim))

            bad = good.astype(complex)
            self.assertEqual(bad.ndim, ndim)
            self.assertTrue(all(np.imag(bad.ravel()) == 0.0))
            self.assertFalse(is_extended_real_numpy_array(bad, ndim))

            bad = good.astype(object)
            self.assertEqual(bad.ndim, ndim)
            self.assertFalse(is_extended_real_numpy_array(bad, ndim))

            # Inject bad elements
            good_flat = copy.deepcopy(good.ravel())
            for i in range(len(good_flat)):
                bad = copy.deepcopy(good_flat)
                bad[i] = np.nan
                bad = bad.reshape(vec_shape)
                self.assertEqual(bad.ndim, ndim)
                self.assertFalse(is_extended_real_numpy_array(bad, ndim))

        # Strange case that might need special handling
        bad = np.full(vec_shape, None)
        self.assertTrue(isinstance(bad.dtype, object))
        self.assertTrue(np.isreal(bad).all())
        with self.assertRaises(TypeError):
            np.isfinite(bad)
        self.assertEqual(bad.ndim, ndim)
        self.assertFalse(is_extended_real_numpy_array(bad, ndim))
