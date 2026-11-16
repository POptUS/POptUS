Variable Check Helpers
======================
.. note::
    This section discusses design motivation and design details for a set of
    helper functions offered by the ``poptus`` package.  This section is,
    therefore, only potentially useful for developers who are considering using
    these helper functions in their codes.

In many situations, Python is a nice language because it is dynamically typed
and often allows for different data structures to functionally behave
identically in certain cases (|eg| iterating over elements in lists, tuples, or
numpy arrays).  However, these aspects can make it difficult to write
maintainable programs as a Python project becomes large or complex.  In such
cases a project can benefit from adopting development philosophies, design
rules, or tools to help limit overuse or unprincipled use of this flexibility.

Some possible best practices to choose from are to

#. Embrace the flexibility by adhering consistently to the philosophy of duck
   typing;
#. Include type hints in Python code and use static analysis tools to confirm
   that variables used during a particular program execution adhere to those
   hints; or
#. Limit argument types to clearly-documented types and explicitly error check
   the types and values of actual arguments at runtime to confirm adherence.

We briefly discuss the advantages and disadvantages of these possibilities as
well as other examples of flexibility to motivate the design of a set of
variable checking helper functions provided in ``poptus``, which method and
model developers can choose to use to help limit the negative impacts of
programmatic flexibility.

Discussion
----------
Duck Typing
^^^^^^^^^^^
While commonly referred to in the early days of Python, the term "duck typing"
is no longer mentioned frequently when developing Python code.  That said, this
technique is likely still used, but potentially without knowing that it has a
name.  This technique can be regarded as a reactive coding style -- use a
variable under the assumption that it is the right type and only react if an
error is raised.

The helper functions take the opposite approach -- proactive determination,
specification, and checking of type and value requirements.

Type Hints
^^^^^^^^^^
.. _`typing`: https://docs.python.org/3/library/typing.html
.. _`type hints`: https://typing.python.org/en/latest/spec/type-system.html

Another likely culprit for the decreased discussion of duck typing is the
*allowance* of type hints in Python code.   Emphasis is placed on "allowance"
since, as stated in the Python `typing`_ documentation,

   The Python runtime does not enforce function and variable type annotations.
   They can be used by third party tools such as type checkers, IDEs, linters,
   etc. 

Effectively, the inclusion of type hints in Python is to enable the Python
interpreter to ignore them.  Therefore, type hints might not be a good option
for codes that need to produce correct results but that cannot presume that
users can or will always run their program with third party confirmation of type
adherence.

The official Python documentation for `type hints`_ includes the statement

    It should also be emphasized that **Python will remain a dynamically typed
    language, and there is no desire to ever make type hints mandatory, even by
    convention**.

(emphasis by bold typeface is copied directly from the Python documentation).
One interpretation of this text is that the use of type hints is outside the
spirit of Python.  In that sense, heavy reliance on type hints to ensure
correctness might suggest the need to search for a better solution or, perhaps,
to choose a different language.

The helper functions enforce explicit type and value checking at runtime with no
extra effort required by users.  It does so within the spirit of the language,
but by following an approach that is sometime criticized as being rooted in the
programming styles of languages such as C and C++.

NumPy
^^^^^
While NumPy is often used for performing linear algebra computations, it's
design is not always natural for working with linear algebra objects.  For
example, NumPy arrays are understandably more closely related to basic,
general-use data structures than vectors and matrices.  This resulted in the
ability to represent in NumPy a linear algebra vector as an

* :math:`n`-element 1D array implementing a vector as a 1D object,
* :math:`1 \times n` 2D array implementing a row vector, or
* :math:`n \times 1` 2D array implementing a column vector,

which is another example of potentially-problematic programmatic flexibility.
For example, some programs adopt mathematical purity and insist that calling
code always pass in a row or column vector, whichever is mathematically correct
for the functionality being called.  However, this burdens developers with
needing to know if a row or a column is required and adapting variables to
match.  These difficulties are significant when a code combines third party
codes that each has their own rigid but different scheme for "vector"
management.

Another option is to allow for calling code to accept a "vector" argument in any
of those three representations and to determine how best to handle that
variability.  One justification for this is the observation that in many
situations the three representations are practically interchangeable when used
to perform linear algebra computations.

The design of these helper functions adopts this latter approach.  To make this
flexibility manageable, it is intended that code also adopt the design rule that
**all** code that accept "vectors" must accept all three representations but
immediately convert those arguments to 1D NumPy arrays so that developers only
have to think in 1D arrays when writing and reviewing code.  This also has the
benefit of not having to worry about transpositions and that all functions and
classes written for only internal use can operate under the assumption that all
actual "vector" arguments are always 1D NumPy arrays.

Intentions
----------
The helper functions are designed with computational math, science, and
engineering programs in mind.  Emphasis has been placed on constraining Python's
and NumPy's inherent flexibility as much as possible without unduly restricting
developer freedom or increasing the risk of errors.  One goal is to avoid
developing code that no developer wants to touch because it's too easy to
introduce undetected bugs (|ie| brittle code).  Rather, the use of the helper
functions and the adoption of its design philosophy should result in clear,
unambiguous failures if anything slightly different from what is expected happens
during execution.

They are also designed as a set so that each implements a similar, simple
interface that is rooted in the mathematical objects that it checks rather in
the Python mechanism used to store and work with their associated quantities.
For example, we refer to "reals" and "extended reals" rather than ``float`` or
``numpy.float32``.  Similarly, where possible we refer to "vectors" and
"matrices", but allow for array arguments that are unrelated to linear algebra.

In the interest of making these functions broadly useful and to decrease the
likelihood that their interface will change in the future, each helper function
simply performs the check referred to in its name and returns a ``bool``.  This
implies that these functions assist in error checking but do not perform any
error checking.  In particular, they should not raise any errors and do not need
to be adapted to a particular error handling scheme.  Instead, calling code must
determine how to communicate to users issues uncovered by the helper functions
as well as how to raise an error if necessary.

Similarly, these functions do not try to "sanitize" the arguments.  For example,
functions like :py:func:`poptus.is_finite_real_numpy_vector` do not convert 2D
NumPy arrays representing row or column vectors into a 1D NumPy array.  Rather,
if it returns ``True`` for a given vector ``x``, then calling code can choose to
explicitly squeeze ``x`` down to a 1D NumPy array and simultaneously decide if
their code should prefer to work with a view or a copy of the original ``x``
argument.

Guidance
--------
Codes that might benefit from using these helpers and their underlying design
philosophy are those that

* work substantially with array variables,
* ultimately uses array variables in computations based in NumPy,
* can and are willing to ask calling code to supply arguments of specific types
  only, and
* can write their computational code such that all "vector" variables are always
  1D NumPy arrays.

In particular, these helpers impose the least effort on developers of programs
that can insist that all actual array arguments be NumPy arrays of a specific
dimension.

Some examples of constraining types are:

* If code requests that an argument be an integer, then it is an error to pass
  any variety of ``float`` even if its contents correspond to an integer (|eg|
  1.0).
* If code requests that an argument be a real vector, then a NumPy vector of
  type ``int`` would not be accepted.  However, any qualifying float type (|eg|
  ``np.float32``) is accepted.

Interface
---------
.. autofunction:: poptus.is_integer
.. autofunction:: poptus.is_finite_real
.. autofunction:: poptus.is_extended_real
.. autofunction:: poptus.is_finite_real_numpy_vector
.. autofunction:: poptus.is_finite_real_numpy_array
.. autofunction:: poptus.is_extended_real_numpy_vector
.. autofunction:: poptus.is_extended_real_numpy_array
