import numbers

import numpy as np


def is_integer(n):
    """
    :return: ``True`` if **n** is an integer variable.  Aside from the obvious
        cases, ``False`` is returned if **n** is a ``bool`` or if **n** is an
        integer value stored in floating point format (|eg| 1.0).
    """
    return isinstance(n, numbers.Integral) and (not isinstance(n, bool))


def is_finite_real(x):
    """
    :return: ``True`` if **x** is a floating point variable whose content is a
        finite real.  Aside from the obvious cases, ``False`` is returned if
        **x** is ``NaN``, ``+/-Inf``, a ``bool``, a complex variable with or
        without an imaginay part, or, for example, any container containing one
        or more finite reals.
    """
    return isinstance(x, numbers.Real) and (not isinstance(x, bool)) and \
        (not np.iscomplexobj(x)) and np.isfinite(x)


def is_extended_real(x):
    """
    :return: ``True`` if **x** is a floating point variable whose content is an
        extended real.  Aside from the obvious cases, ``False`` is returned if
        **x** is ``NaN``, a complex variable with or without an imaginay part,
        or, for example, any container containing one or more extended reals.
    """
    return isinstance(x, numbers.Real) and (not isinstance(x, bool)) and \
        (not np.iscomplexobj(x)) and (not np.isnan(x))


def is_finite_real_numpy_vector(x):
    r"""
    :return: ``True`` if **x** is an :math:`n` element 1D NumPy array, a
        :math:`1 \times n` 2D NumPy array, or a :math:`n \times 1` 2D NumPy
        array whose elements are all finite real.  Aside from the obvious cases,
        ``False`` is returned if any of the elements are ``NaN``, ``+/-Inf``, or
        complex variables with or without imaginary parts.  Note that while
        :math:`n = 1` is acceptable, **x** must still be an appropriately-shaped
        1D or 2D NumPy array.
    """
    # issubdtype is required because, for example,
    #                     np.isreal(np.full(5, None))
    # returns all True.
    #
    # I don't believe that isreal() is needed since we check that dtype of the
    # array is floating, but not complex.
    x_1d = np.atleast_1d(np.squeeze(x))
    return isinstance(x, np.ndarray) and (x.ndim in {1, 2}) and \
        (x_1d.ndim == 1) and (len(x_1d) > 0) and \
        np.issubdtype(x.dtype, np.floating) and (not np.iscomplexobj(x)) and \
        np.isfinite(x).all()


def is_extended_real_numpy_vector(x):
    r"""
    :return: ``True`` if **x** is an :math:`n` element 1D NumPy array, a
        :math:`1 \times n` 2D NumPy array, or a :math:`n \times 1` 2D NumPy
        array whose elements are all extended real.  Aside from the obvious
        cases, ``False`` is returned if any of the elements are ``NaN`` or
        complex variables with or without imaginary parts.  Note that while
        :math:`n = 1` is acceptable, **x** must still be an appropriately-shaped
        1D or 2D NumPy array.
    """
    # issubdtype is required because, for example,
    #                     np.isreal(np.full(5, None))
    # returns all True.
    #
    # I don't believe that isreal() is needed since we check that dtype of the
    # array is floating, but not complex.
    x_1d = np.atleast_1d(np.squeeze(x))
    return isinstance(x, np.ndarray) and (x.ndim in {1, 2}) and (x_1d.ndim == 1) and \
        np.issubdtype(x.dtype, np.floating) and (not np.iscomplexobj(x)) and \
        (not np.isnan(x).any())


def is_finite_real_numpy_array(x, ndim):
    """
    :param: A positive integer greater than one that indicates the required
        dimension of **x**.
    :return: ``True`` if **x** is a NumPy array of dimension **ndim** whose
        elements are all finite real.  Aside from the obvious cases, ``False``
        is returned if any of the elements are ``NaN``, ``+/-Inf``, or complex
        variables with or without imaginary parts.  It also returns ``False`` if
        the array is the wrong dimension even though it could be correctly
        squeezed or extended to **ndim**.
    """
    # issubdtype is required because, for example,
    #                     np.isreal(np.full(5, None))
    # returns all True.
    #
    # I don't believe that isreal() is needed since we check that dtype of the
    # array is floating, but not complex.

    # Assert rather than error check/raise error since only developers should be
    # calling this.  In other words, with the help of this assert developers
    # should quickly settle on code that calls this check correctly.
    assert ndim > 1
    return isinstance(x, np.ndarray) and (x.ndim == ndim) and \
        np.issubdtype(x.dtype, np.floating) and (not np.iscomplexobj(x)) and \
        np.isfinite(x).all()


def is_extended_real_numpy_array(x, ndim):
    """
    :param: A positive integer greater than one that indicates the required
        dimension of **x**.
    :return: ``True`` if **x** is a NumPy array of dimension **ndim** whose
        elements are all in the extended reals.  Aside from the obvious cases,
        ``False`` is returned if any of the elements are ``NaN`` or complex
        variables with or without imaginary parts.  It also returns ``False`` if
        the array is the wrong dimension even though it could be correctly
        squeezed or extended to **ndim**.
    """
    # issubdtype is required because, for example,
    #                     np.isreal(np.full(5, None))
    # returns all True.
    #
    # I don't believe that isreal() is needed since we check that dtype of the
    # array is floating, but not complex.

    # Assert rather than error check/raise error since only developers should be
    # calling this.  In other words, with the help of this assert developers
    # should quickly settle on code that calls this check correctly.
    assert ndim > 1
    return isinstance(x, np.ndarray) and (x.ndim == ndim) and \
        np.issubdtype(x.dtype, np.floating) and (not np.iscomplexobj(x)) and \
        (not np.isnan(x).any())
