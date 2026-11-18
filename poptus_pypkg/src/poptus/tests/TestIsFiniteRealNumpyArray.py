import copy
import unittest
import warnings

import numpy as np

from poptus.tests._constants import (
    FINITE_REALS,
    NOT_NUMPY_ARRAY
)
from poptus._variable_checks import (
    is_finite_real_numpy_vector,
    is_finite_real_numpy_array
)


class TestIsFiniteRealNumpyArray(unittest.TestCase):

    def setUp(self):
        self.__N_TO_TEST = {2, 3, 5, 10}
        self.__NDIMS_TO_TEST = {2, 3, 4}

    def testNotArrays(self):
        # Test only on acceptable dimensions even though these arguments have
        # nothing generally to do with dimensions
        for ndim in self.__NDIMS_TO_TEST:
            for bad in NOT_NUMPY_ARRAY:
                self.assertFalse(is_finite_real_numpy_array(bad, ndim))

            for good_real in FINITE_REALS:
                bad_types = [
                    good_real, str(good_real),
                    good_real + 1j, good_real + 0.0 * 1j,
                    (good_real), (good_real,),
                    [good_real], [[good_real]], {good_real}, {"bad": good_real}
                ]
                for bad in bad_types:
                    self.assertFalse(is_finite_real_numpy_array(bad, ndim))

    def test0dArrays(self):
        NDIM = 0

        # 0D arrays are strange, so check this carefully
        for good_real in FINITE_REALS:
            good_0d = np.array(good_real)
            self.assertTrue(isinstance(good_0d, np.ndarray))
            self.assertEqual(good_0d.ndim, NDIM)
            self.assertTrue(np.isreal(good_0d))
            self.assertTrue(np.isfinite(good_0d))
            self.assertEqual(good_0d, good_real)
            self.assertEqual(np.squeeze(good_0d), good_real)

            with self.assertRaises(AssertionError):
                self.assertFalse(is_finite_real_numpy_array(good_0d, NDIM))

    def test1dArrays(self):
        NDIM = 1

        for good_real in FINITE_REALS:
            bad = np.array([good_real])
            self.assertEqual(bad.ndim, NDIM)
            self.assertTrue(is_finite_real_numpy_vector(bad))

            with self.assertRaises(AssertionError):
                self.assertFalse(is_finite_real_numpy_array(bad, NDIM))

            bad = np.full(5, good_real)
            self.assertEqual(bad.ndim, NDIM)
            self.assertTrue(is_finite_real_numpy_vector(bad))

            with self.assertRaises(AssertionError):
                self.assertFalse(is_finite_real_numpy_array(bad, NDIM))

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
            self.__testArray((1, N, 2))
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

        for good_real in FINITE_REALS:
            good = np.full(vec_shape, good_real)
            self.assertEqual(good.dtype, np.float64)
            self.assertEqual(good.ndim, ndim)
            self.assertTrue(is_finite_real_numpy_array(good, ndim))
            for bad in self.__NDIMS_TO_TEST.difference({ndim}):
                self.assertFalse(is_finite_real_numpy_array(good, bad))

            # Confirm that the helpers accept different float types
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "overflow encountered in cast")

                for floating in [np.float16, np.float32]:
                    goodish = np.full(vec_shape, good_real, floating)
                    if floating(good_real) == np.inf:
                        self.assertFalse(is_finite_real_numpy_array(goodish, ndim))
                    else:
                        self.assertTrue(is_finite_real_numpy_array(goodish, ndim))

                    goodish = np.full(vec_shape, -good_real, floating)
                    if floating(-good_real) == -np.inf:
                        self.assertFalse(is_finite_real_numpy_array(goodish, ndim))
                    else:
                        self.assertTrue(is_finite_real_numpy_array(goodish, ndim))

            self.assertFalse(is_finite_real_numpy_array(good.tolist(), ndim))
            self.assertFalse(is_finite_real_numpy_array(tuple(good.tolist()), ndim))

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "invalid value encountered in cast")

                bad = good.astype(int)
                self.assertEqual(bad.ndim, ndim)
                self.assertFalse(is_finite_real_numpy_array(bad, ndim))

            bad = good.astype(str)
            self.assertEqual(bad.ndim, ndim)
            self.assertFalse(is_finite_real_numpy_array(bad, ndim))

            bad = good.astype(complex)
            self.assertEqual(bad.ndim, ndim)
            self.assertTrue(all(np.imag(bad.ravel()) == 0.0))
            self.assertFalse(is_finite_real_numpy_array(bad, ndim))

            bad = good.astype(object)
            self.assertEqual(bad.ndim, ndim)
            self.assertFalse(is_finite_real_numpy_array(bad, ndim))

            # Inject bad elements
            good_flat = good.ravel()
            for i in range(len(good_flat)):
                for bad_real in {np.nan, np.inf, -np.inf}:
                    bad = copy.deepcopy(good_flat)
                    bad[i] = bad_real
                    bad = bad.reshape(vec_shape)
                    self.assertEqual(bad.ndim, ndim)
                    self.assertFalse(is_finite_real_numpy_array(bad, ndim))

        # Strange case that might need special handling
        bad = np.full(vec_shape, None)
        self.assertTrue(isinstance(bad.dtype, object))
        self.assertTrue(np.isreal(bad).all())
        with self.assertRaises(TypeError):
            np.isfinite(bad)
        self.assertEqual(bad.ndim, ndim)
        self.assertFalse(is_finite_real_numpy_array(bad, ndim))
