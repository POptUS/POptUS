import sys

import numpy as np

# Set these to match standard Python int
GOOD_INTEGERS = [-sys.maxsize, -1001, -1, 0, 1, 27, 25_234, sys.maxsize]
NOT_INTEGER = [
    None, "", "not_an_int", True, False, 1.1,
    1j, (0.0 * 1j), np.nan, np.inf, -np.inf,
    (), [], set(), {}, object
]

# Intentionally set to interesting nonnegative values with type set to np.float64.
FINITE_REALS = [
    np.float64(0.0), np.float64(1.0), np.float64(1.1),
    np.finfo(float).smallest_normal, np.finfo(float).max,
    np.finfo(float).eps, 1.0 + np.finfo(float).eps
]
NOT_FINITE_REAL = [
    None, "", "not_finite_real", True, False,
    1j, (0.0 * 1j), np.nan, np.inf, -np.inf,
    (), [], set(), {}, object
]

# Intentionally set to interesting nonnegative values (excluding -inf)
# with type set to np.float64.
EXTENDED_REALS = FINITE_REALS + [np.float64(np.inf), np.float64(-np.inf)]
NOT_EXTENDED_REAL = [r for r in NOT_FINITE_REAL if r not in [np.inf, -np.inf]]

NOT_NUMPY_ARRAY = [
    None, "", "not_array", True, False, 0, 1, 0.0, 1.0, 1.1,
    1j, (0.0 * 1j), np.nan, np.inf, -np.inf,
    (), [], set(), {}, object
]
