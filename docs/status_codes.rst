Status Codes
============
|poptus| is where a model meets a method.  Since those two elements are likely
written by different teams and methods should be developed to work with as many
different models as possible, |poptus| includes a standard for communicating
error conditions encountered during model execution to the methods that prompted
that execution.  In the simplest case, a method should terminate its execution
to avoid wasting computational resources if a model communicates that the
quality of a critical result is poor.  Therefore, this |poptus| standard insists
that all model results be accompanied by a status code that indicates the
quality of the result as determined by the model's developers.

Status codes are also valuable since their use and writing to file aid
|poptus|-based studies in achieving correctness and rigor.  Similarly, they can
aid in testing and debugging codes.  In this spirit, |poptus| methods also
assign status codes to their own computational results as determined by each
method's developers.

Even though the standard helps decouple the model from the methods while
ensuring correct communication of computation quality, it cannot fully overcome
the difficulties and uncertainties that arise.  As emphasized above,

* assignment of status codes to model values is done by model developers,
* assignment of status codes to method values is done by method developers,
  and
* method developers decide how to use and react to obtaining results with status
  codes other than valid.

Since model and method developers cannot make their decisions within the context
of each user's study, it's ultimately up to users to interpret method and model
results within the context of the status codes as well as the determination and
use of these.  By archiving status codes with their results, we hope to help
users understand what quantities should be reviewed and make it easy to do so.
In addition, |poptus| methods document how and when they assign the different
status codes to their results as well as how their methods use model status
codes internally to guide their execution.

Specification
-------------
|poptus| provides and works with the status codes

* ``poptus.STATUS_VALID``,
* ``poptus.STATUS_MARGINAL``,
* ``poptus.STATUS_INVALID``,
* ``poptus.STATUS_CANCELED``, and
* ``poptus.STATUS_FAILED``,

which are assigned constant integer values that respect the ordering

.. math::

    \mathrm{Valid} < \mathrm{Marginal} <
    \mathrm{Invalid} < \mathrm{Canceled} <
    \mathrm{Failed}.

Otherwise, the actual integer values assigned to the constants are unimportant.
A status code should be considered as "more serious" than all status codes with
smaller values.

To help clarify the definitions of the different status codes, we will consider
the example of a simulation code that computes theoretical values for a
particular physical quantity using an iterative solver provided with a stopping
criterion and a maximum number of iterations it can use to approximate the
theoretical value.

A computational result is **valid** if its computation successfully ran to
completion with no indication of error.  If our iterative solver approximates
the desired theoretical result within its stopping criterion and its iteration
budget (|ie| the computation successfully converged), then the result's status
code should be ``poptus.STATUS_VALID``.

A computational result is **marginal** if its computation yielded a value that
cannot be marked as ``poptus.STATUS_VALID``, but is believed to be reasonably
close to what would be a "valid" result.  If the iterative solver does not
converge within its stopping criterion and its iteration budget, then the
solver's developers might decide that the result is marginal if

* the last :math:`N` iterations were just above the stopping criterion and slowly
  marching toward the criterion and
* the solver's approximation to the physical quantity did not change
  appreciably over the last :math:`N` iterations.

A computational result is **invalid** if its computation terminated but yielded
a value that should be considered as incorrect.  This could occur, for example,
if

* the iterative solver failed to converge within its allotted budget and
  analysis of the last :math:`N` iterations do not indicate a nearly convergent
  process,
* an anomalous event occurred during an otherwise successful, convergent
  computation that casts doubt on the validity of the result, or
* the result is nonsensical (|eg| a negative radius) or not physically sensible
  (|eg| a radius that is unreasonably large even within the limitations of the
  underlying model).

A computational result is marked as **canceled** if its computation was canceled
outside of normal model execution by some entity.  This could be due to, for
example,

* a user manually terminating the computation or
* the method or model automatically terminating the computation to save
  resources because the computation was deemed useless due to the concurrent
  computation of a related quantity yielding an unacceptable result.

A computational result is marked as **failed** if its computation terminated due
to a failure in the solver itself rather than |via| a normal execution path.
For instance, a result obtained by a noncovergent execution of the solver should
be marked as ``poptus.STATUS_INVALID``.  However, the result should be marked as
``poptus.STATUS_FAILED`` if the solver terminated before exceeding its budget
due to an internal runtime failure or if an intermediate or internal result
indicated an algorithmic failure.

.. todo::
    Should "nonsensical" and "unphysical" be added as statuses between marginal
    and invalid?  Nonsensical would be worse than unphysical.  The argument for
    including these is that these two classifications would break out suspicious
    or unacceptable convergent results.  In addition, they would allow for
    offline analysis to classify results at a finer level, which could aid error
    analysis and result verification.  One difficulty with this is how methods
    would use these.  For instance, they would likely treat nonsensical as they
    do invalid.  But what about unphysical?  In some circumstances an unphysical
    result does not mean an invalid computation.  For instance an optimization
    could wander into a region where correct, valid computations yield
    unphysical results.  That doesn't mean the optimization should terminate
    since it might eventually wander back into a region that yields physical
    results.

Examples
--------
If a method uses a model to evaluate a function at three neighboring points so
that it can approximate the second derivative of the function at the central
point, then it would be sensible to set the status code of the approximation to
the maximum value of the status codes for the three model evaluations.  However,
this rule should also consider the possibility that the computation of the
approximation could fail.  A status code of ``poptus.STATUS_INVALID`` might be
assigned to the approximation if all three evaluations were valid or marginal
but the computation of the approximation yielded :math:`\pm \infty`.

To help explain the potential utility of marking some results as marginal,
consider a method that would like to increase the likelihood of obtaining a
valid solution even when used with a model that often produces invalid results.
Suppose further, that the developer of one such model is willing and able to
reclassify some invalid results as marginal.  The method could be developed so
that marginal results can be tolerated when collected for certain noncritical
intermediate or internal purposes, but result in aborted method execution when
collected at certain critical points.  For example, marginal results might be
acceptable when collecting data needed to build rough internal models, but be
rejected if the results would be used directly to compute a solution.
Similarly, an iterative method might continue execution as usual if one or more
marginal results are collected, but counsel its users to never consider an
iteration's result as a valid solution if its result or the results of
neighboring iterations were derived using marginal results.

Model Developers
----------------
Since the use of status codes is specified at the level of |poptus|, a model
developer should be able to adapt their model code (or wrap calls to their model
code in a function) to provide a |poptus|-compatible interface that will
work with all methods in the |poptus| universe.

Practically speaking this means that their programmatic implementation of their
:math:`\mathbf{F} : \mathbb{R}^n \to \mathbb{R}^d` black box function must
return both the vector result as well as an individual status code for each
element in that vector.

.. todo::
    Write a separate section in the User Guide the presents :math:`\mathbf{F}`
    mathematically as well as its expected programmatic interface.  This would
    likely appear in a discussion of the |poptus| Model abstract base class.  We
    could link to that here to provide concrete standard information.
