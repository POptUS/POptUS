Logging
=======

The experience of developing a code that uses |poptus| logging is different from
the experience of using a code that was implemented with |poptus| logging.
While the first section might be useful for all users, the second is targeted
just for developers.

Using loggers in applications
-----------------------------
Codes that use the |poptus| logging functionality generally accept a logger
object that has been configured as desired by an application or individual user.
These objects are typically configured and created using the
:py:func:`poptus.create_logger` function.  A particularly important example of a
logger configuration value is the logger's verbosity level.  Note that some
codes might require that users only provide a configuration data structure and
will create a logger object on the user's behalf.

Each code passes individual messages to its logger with a potentially
different verbosity level for each message.  While warning and error log
messages are always logged by |poptus|, the logger only logs those general and
debug information messages whose verbosity level is compatible with the logger's
verbosity level.

Valid logger verbosity levels and their associated logging output are

* ``LOG_LEVEL_NONE`` - only warnings and errors
* ``LOG_LEVEL_DEFAULT`` - general information, warnings, and errors
* ``LOG_LEVEL_MIN_DEBUG`` - general information, minimal debug information,
  warnings, and errors

Larger levels up to and including ``LOG_LEVEL_MAX`` may be specified with more
debug information being logged as the level increases.

Each code also provides its logger with a (hopefully) unique name so that its
messages all start with this name.  This is important for applications that have
multiple codes logging messages to the same output since users should,
therefore, be able to use tools such as ``grep`` to filter out messages from
just one source.

Loggers always identically prepend the word "WARNING" to all warning messages
and "ERROR" to all error messages.  Therefore, users should be able to quickly
and effectively identify all warning or error messages in log output.

Consider the example log output written to the file ``study.log``

.. code:: console

    [Model] message a
    [Model] message b
    [Method] WARNING - message 1
    [Model] message c
    [Model] WARNING - message d
    [Method] message 2
    [Model] ERROR - message e

which we imagine was produced by a Model and a Method code, both logging
different types of messages to the file.  The command

.. code:: console

    grep WARNING study.log

filters out all warning messages.  The command

.. code:: console

    grep WARNING study.log | grep "\[Model\]"

filters out only those warning messages produced by the Model code.

Logging to Standard Output/Error
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The creation of a standard output/error logger requires only the specification
of the logger's desired verbosity  ``Level``, which must be one of the above
valid values.  The code

.. code:: python

    import poptus

    configuration = {"Level": poptus.LOG_LEVEL_DEFAULT}
    logger = poptus.create_logger(configuration)

creates a standard output/error logger that writes

* general information and warnings to standard output,
* errors to standard error, and
* suppresses the logging of all debug information.

If logging of one or more levels of debug information is compatible with the
logger's verbosity level, then such information is written to standard output.

Logging to File
^^^^^^^^^^^^^^^
File loggers require the specification of ``Filename`` and ``Overwrite`` values
in addition to ``Level``.  The code

.. code:: python

    import poptus

    configuration = {
        "Level": poptus.LOG_LEVEL_MIN_DEBUG+1,
        "Filename": "/path/to/study.log",
        "Overwrite": True
    }
    logger = poptus.create_logger(configuration)

creates a file logger that writes general information, two levels of debug
information, warnings, and errors to the file ``study.log``, which it will
overwrite if necessary.  Note that all error messages are also written to
standard error.

Mulitple Loggers
^^^^^^^^^^^^^^^^
For applications comprised of two or more codes using |poptus| logging, it might
be useful to configure a different logger for each code.  For example, the code

.. code:: python

    import poptus

    model_cfg = {"Level": poptus.LOG_LEVEL_DEFAULT}
    method_cfg = {
        "Level": poptus.LOG_LEVEL_MIN_DEBUG+1,
        "Filename": "/path/to/method.log",
        "Overwrite": True
    }
    model_logger = poptus.create_logger(model_cfg)
    method_logger = poptus.create_logger(method_cfg)

creates two distinct loggers with method information written to file with high
verbosity and model information written to standard output/error with low
verbosity.

Custom Loggers
^^^^^^^^^^^^^^

.. todo::

    Determine if customization is possible and desired.  If not desired,
    determine if the design can at least leave the door open to customization.

Developers using |poptus|
-------------------------
.. _`xSDK requirement`: https://xsdk.info/policies
.. _`look and feel`: https://en.wikipedia.org/wiki/Look_and_feel

The |poptus| logging facilities have been designed so that methods that restrict
all logging activities to using these facilities will satisfy a mandatory `xSDK
requirement`_.  Therefore, all |poptus| methods should use these logging
facilities so that |poptus| can qualify for inclusion in the xSDK community.
This requirement has the side effect of providing for users a common `look and feel`_ 
in terms of logging configuration and use.  Importantly, a common look and feel
should also simplify and aid |poptus| development and maintenance.

Since |poptus| loggers automatically include the word "WARNING" in all warning
outputs and "ERROR" in all error outputs, there is no need for developers to
include either of these words or anything similar in their warning and error
messages.  It's important that all log and debug messages be chosen to allow for
users to filter out all warning or error messages correctly without
accidentally including general or debug messages in their filtered output.

Similarly, codes should prefer uncommon or detailed names for prepending to
messages to facilitate effective filtering of messages.  For example, a model
code should avoid using "Model" as its logging name since a method could
conceivably and reasonably include that word in its log messages.  This
suggestion should also decrease the likelihood of two different codes in a
single application logging messags with the same log name.

.. todo::

    Include link to examples in Jupyter book once that exists.
