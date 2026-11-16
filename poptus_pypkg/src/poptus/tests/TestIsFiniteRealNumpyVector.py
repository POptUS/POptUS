import copy
import unittest
import warnings

import numpy as np

from poptus.tests._constants import (
    FINITE_REALS, NOT_FINITE_REAL,
    NOT_NUMPY_ARRAY
)
from poptus._variable_checks import (
    is_finite_real_numpy_vector,
    is_finite_real_numpy_array
)


class TestIsFiniteRealNumpyVector(unittest.TestCase):

    def setUp(self):
        self.__NDIMS_TO_TEST = {2, 3, 5, 10}

    def testNotArrays(self):
        for bad in NOT_NUMPY_ARRAY:
            self.assertFalse(is_finite_real_numpy_vector(bad))

        for good_real in FINITE_REALS:
            self.assertFalse(is_finite_real_numpy_vector(good_real))
            bad = str(good_real)
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = good_real + 1j
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = good_real + 0.0 * 1j
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = (good_real)
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = (good_real,)
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = [good_real]
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = [[good_real]]
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = {good_real}
            self.assertFalse(is_finite_real_numpy_vector(bad))
            bad = {"bad": good_real}
            self.assertFalse(is_finite_real_numpy_vector(bad))

    def test0dArrays(self):
        # 0D arrays are strange, so check this carefully
        for good in FINITE_REALS:
            good_0d = np.array(good)
            self.assertTrue(isinstance(good_0d, np.ndarray))
            self.assertEqual(good_0d.ndim, 0)
            self.assertTrue(np.isreal(good_0d))
            self.assertTrue(np.isfinite(good_0d))
            self.assertEqual(np.squeeze(good_0d), good)

            self.assertFalse(is_finite_real_numpy_vector(good_0d))

    def testAllVectorTypes(self):
        self.__testVector((1,))
        self.__testVector((1, 1))

        for N in self.__NDIMS_TO_TEST:
            self.__testVector((N,))
            self.__testVector((N, 1))
            self.__testVector((1, N))

    def __testVector(self, vec_shape):
        ndim = len(vec_shape)
        self.assertTrue(ndim in {1, 2})

        N = np.max(vec_shape)

        for good_real in FINITE_REALS:
            good = np.full(vec_shape, good_real)
            self.assertEqual(good.dtype, np.float64)
            self.assertEqual(good.ndim, ndim)
            if N > 1:
                self.assertEqual(np.squeeze(good).ndim, 1)
                self.assertEqual(len(np.squeeze(good)), N)
            else:
                self.assertEqual(good.ndim, ndim)
                self.assertEqual(len(good), 1)
            self.assertTrue(is_finite_real_numpy_vector(good))

            good = np.full(vec_shape, -good_real)
            self.assertTrue(is_finite_real_numpy_vector(good))

            # Confirm that the helpers accepts different float types
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "overflow encountered in cast")

                for floating in [np.float16, np.float32]:
                    goodish = np.full(vec_shape, good_real, floating)
                    if floating(good_real) == np.inf:
                        self.assertFalse(is_finite_real_numpy_vector(goodish))
                    else:
                        self.assertTrue(is_finite_real_numpy_vector(goodish))

                    goodish = np.full(vec_shape, -good_real, floating)
                    if floating(-good_real) == -np.inf:
                        self.assertFalse(is_finite_real_numpy_vector(goodish))
                    else:
                        self.assertTrue(is_finite_real_numpy_vector(goodish))

            self.assertFalse(is_finite_real_numpy_vector(good.tolist()))
            self.assertFalse(is_finite_real_numpy_vector(tuple(good.tolist())))

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "invalid value encountered in cast")

                bad = good.astype(int)
                self.assertFalse(is_finite_real_numpy_vector(bad))

            bad = good.astype(str)
            self.assertFalse(is_finite_real_numpy_vector(bad))

            bad = good.astype(complex)
            self.assertTrue(all(np.imag(bad.ravel()) == 0.0))
            self.assertFalse(is_finite_real_numpy_vector(bad))

            bad = good.astype(object)
            self.assertFalse(is_finite_real_numpy_vector(bad))

            # Inject bad elements
            for i in range(N):
                for bad_real in {np.nan, np.inf, -np.inf}:
                    bad = copy.deepcopy(np.atleast_1d(np.squeeze(good)))
                    bad[i] = bad_real
                    bad = bad.reshape(vec_shape)
                    self.assertEqual(bad.ndim, ndim)
                    self.assertFalse(is_finite_real_numpy_vector(bad))

        if N == 1:
            for bad_real in NOT_FINITE_REAL:
                bad = np.array([bad_real])
                self.assertFalse(is_finite_real_numpy_vector(bad))
        else:
            # Strange case that might need special handling
            bad = np.full(vec_shape, None)
            self.assertEqual(bad.ndim, ndim)
            self.assertEqual(np.squeeze(bad).ndim, 1)
            self.assertEqual(len(np.squeeze(bad)), N)
            self.assertEqual(bad.dtype, object)
            self.assertTrue(np.isreal(bad).all())
            with self.assertRaises(TypeError):
                np.isfinite(bad)
            self.assertFalse(is_finite_real_numpy_vector(bad))

    def test2dArrays(self):
        for N in self.__NDIMS_TO_TEST:
            for good_real in FINITE_REALS:
                bad = np.full((N, 2), good_real)
                self.assertEqual(bad.ndim, 2)
                self.assertTrue(is_finite_real_numpy_array(bad, 2))
                self.assertFalse(is_finite_real_numpy_vector(bad))

    def test3dArrays(self):
        for N in self.__NDIMS_TO_TEST:
            for good_real in FINITE_REALS:
                # Single-element 3D arrays
                bad = np.array([[[good_real]]])
                self.assertEqual(bad.shape, (1, 1, 1))
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))

                # 3D row and column vectors
                bad = np.full((N, 1, 1), good_real)
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))

                bad = np.full((1, N, 1), good_real)
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))

                bad = np.full((1, 1, N), good_real)
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))

                # 3D matrices
                bad = np.full((N, 2, 1), good_real)
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))

                bad = np.full((N, 1, 2), good_real)
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))

                bad = np.full((1, N, 2), good_real)
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))

                # 3D array
                bad = np.full((N, 2, 2), good_real)
                self.assertTrue(is_finite_real_numpy_array(bad, 3))
                self.assertFalse(is_finite_real_numpy_vector(bad))
