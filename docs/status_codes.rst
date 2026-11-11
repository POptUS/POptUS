Status Codes
============
|poptus| is where a model meets a method.  Since those two elements are likely
written by different teams and methods should be developed to work with an many
different models as possible, |poptus| includes a standard for communicating
error conditions encountered during model execution to the methods that prompted
that execution.  In the simplest case, a method should terminate its execution
to avoid wasting computational resources if a model communicates that the
quality of a critical result is suspect.  To accomplish this, |poptus| insists
that all model results be accompanied by a status code that indicates if it is
valid or invalid.

Status codes are also useful since their use and recording improve the
correctness of and the rigor of |poptus|-based studies.  Similarly, they can aid
in testing and debugging codes.  In this spirit, |poptus| methods also benefit
from assigning status codes to their own computational results.

|poptus| provides and works with the status codes

* ``poptus.STATUS_VALID``
* ``poptus.STATUS_MARGINAL``
* ``poptus.STATUS_INVALID``
* ``poptus.STATUS_CANCELED``
* ``poptus.STATUS_FAILED``,

which are effectivaly macros for integers that respect the ordering

.. math::

    \mathrm{Valid} < \mathrm{Marginal} <
    \mathrm{Invalid} < \mathrm{Canceled} <
    \mathrm{Failed}.

Otherwise, the actual integer values of the different macros are unimportant.  A
status code should be considered as "more serious" than all status codes with
smaller values.

To help clarify the definitions of the different status codes, we will consider
the example of a simulation code that computes theoretical values for a
particular physical quantity using an iterative solver programmed with a
stopping criteria and limited to approximate the theoretical value within a
given number of iterations.

A computational result is **valid** if its computation successfully ran to
completion with no indication of error.  If our iterative solver approximates
the desired theoretical result within its stopping criteria and its iteration
budget (|ie| the computation successfully converged), then the result's status
code should be ``poptus.STATUS_VALID``.

A computational result is **marginal** if its computation yielded a value that
cannot be marked as ``poptus.STATUS_VALID``, but that is believed to be
reasonably close to what would be a "valid" result.  If the iterative solver
does not converge within its stopping criteria and its iteration budget, then
the solver's developers might decide that the result is marginal if

* the last 100 iterations were just above the stopping criteria and slowly
  marching toward the criteria and
* the solver's results were not changing appreciably over the last 100
  iterations.

A computational result is **invalid** if its computation terminated but yielded
a value that should be considered as incorrect.  This could occur, for example,
if

* the iterative solver failed to converge within its allotted budget,
* an anamolous event occurred during an otherwise successful, convergent
  computation that casts doubt on the validity of the result, or
* the result is nonsensical (|eg| a negative radius) or not physically sensible
  (|eg| a radius that is unreasonably large even within the limitations of the
  underlying model).

A computational result is marked as **canceled** if its computation did not
terminate because it was canceled by some entity.  This could be due to, for
example,

* a user manually terminated the computation or
* the method or model automatically terminated the computation to save
  resources because the concurrent computation of a related result was
  found to be unacceptable for some reason.

A computational result is marked as **failed** if its computation terminated due
to a failure in the solver itself rather than |via| a normal execution path.
For instance, a result obtained by a noncovergent execution of the solver should
be marked as ``poptus.STATUS_INVALID``.  However, the result should be marked as
``poptus.STATUS_FAILED`` if the solver terminated before exceeding its budget
due to an internal runtime failure or if an intermediate or internal result
indicated an algorithmic failure.

Model Developers
----------------
Since the use of status codes is specified at the level of |poptus|, a model
developer should be able to adapt their model code (or wrap calls to their model
code in a function) to provide a |poptus|-compatible interface that will
work with all methods in the |poptus| universe.

Practically speaking this means that ...

Method Developers
-----------------
A clear goal of |poptus| is to allow model developers to adapt their model code
to |poptus| standards so that if their model works with one |poptus| method it
will work with all |poptus| methods.  Therefore, it's important that all method
developers work with and provide status codes in the "|poptus| way".

Since the assignment of status codes to all results provided by a model are
determined by model developers, methods should assume that those determinations
are correct and use them blindly -- ultimately it's up to the users to interpret
the method results based on how this mapping is done and how the method uses
status codes.

Therefore, methods that provide their own computational results derived from
model results should also assign status codes to those values.  In addition,
they should clearly document how those status codes are determined and provide,
where possible, indications for how to correctly work with data based in the
context of their status codes.

For example, if a method uses a model to evaluate a function at three
neighboring points so that it can approximate the second derivative of the
function at the central point, then it would be sensible to set the status code
of the approximation to the maximum value of the status codes for the three
model evaluations.  However, this rule should also consider the possibility that
the computation of the approximation could fail.  A status code of
``poptus.STATUS_INVALID`` might be assigned to the approximation if all three
evaluations were valid but the computation of the approximation yielded
:math:`\pm \infty`.

As another example and to help explain the potential utility of marking some
results as marginal, consider a method that wants to increase the likelihood of
obtaining a valid result when used with a model that often produces invalid
results.  Suppose further, that developer of such models are willing or able to
reclassify some invalid results as marginal.  The method could be developed so
that marginal results can be tolerated when collected for certain noncritical
intermediate or internal purposes, but result in aborting method execution when
collected at certain critical points.  They might be acceptable when collecting
data needed to build rough models, but be rejected if the results are used
directly to compute a solution.  Similarly, an iterative method might continue
execution as usual if one or more marginal results are collected, but counsel
its users to never consider an iteration's result as a valid if its solution or
solutions at nearby points were derived using marginal results.
