Logging
=======

|poptus| logging facilities allow for logging to either

* standard output/standard error or
* to a file.

For the former, all warnings are written to standard output and all errors are
written to standard error.  Depending on the verbosity level of the logger,
general information and various levels of debugging information may be written
to standard output.  The code

.. code:: python

    import poptus

    configuration = {"Level": 1}
    logger = poptus.create_logger(configuration)

creates a logger that writes general information and warnings to standard
output.  All errors are written to standard error.  Logging of all debug
information is suppressed.

Valid logging levels correspond to logging

* ``0`` - only warning and errors
* ``1`` - general information, warnings, and errors
* ``2`` - general information, minimal debug information, warnings, and errors

Larger levels up to ``4`` more be specified with more debug information being
logged as the level increases.

When logging to file, all warnings and errors are written to file regardless of
the logger's verbosity level.  In addition, error messages are always written to
standard error.  Depending on the verbosity level of the logger, general
information and various levels of debugging information may be written to the
file as well.  The code

.. code:: python

    import poptus

    configuration = {
        "Level": 3,
        "Filename": "/path/to/method.log",
        "Overwrite": True
    }
    logger = poptus.create_logger(configuration)

creates a logger that writes general information, two levels of debug
information, warnings, and errors to the file ``method.log``, which it will
overwrite if necessary.  The ``Level`` specification is the same as for standard
output/error logging.

It's possible that an application that uses |poptus| methods might use multiple
|poptus| loggers, each of which would require separate configurations.  For
example, an application might require one logger for logging method information
and a separate logger for logging a model's information.  The code

.. code:: python

    import poptus

    method_cfg = {
        "Level": 3,
        "Filename": "method.log",
        "Overwrite": True
    }
    model_logger = poptus.create_logger({"Level": 1})
    method_logger = poptus.create_logger(method_cfg)

creates two such loggers with method information written to file with high
verbosity and model information written to standard output/error will low
verbosity.

While some |poptus| methods might require passing a logger object as an
argument, others might require only a configuration data structure and will
create a logger object on the user's behalf.

Loggers always include the word "WARNING" at the beginning of all warning
messages and "ERROR" at the beginning of all errors messages.  Therefore, users
should be able to quickly and effectively identify (|eg| with ``grep``) all
warning or error messages in log output such as

.. code:: console

    [Model] Debug information level 4 message
    [Model] General information message
    [Method] WARNING - message
    [Model] Debug information level 2 message
    [Model] WARNING - message
    [Method] Debug information level 3 message
    [Model] ERROR - message


Method & Model Developers
-------------------------
.. _`xSDK requirement`: https://xsdk.info/policies

The |poptus| logging facilities have been designed so that methods that restrict
all logging activities to using these facilities will satisy a mandatory `xSDK
requirement`_.  Therefore, all |poptus| methods should use these logging
facilities so that |poptus| can qualify for inclusion in the xSDK community.
This requirement has the side effect of providing for users a common look & feel
in terms of logging configuration and use.  Importantly, it should also simplify
and aid |poptus| development and maintenance.

Since |poptus| loggers automatically include the word "WARNING" in all warning
outputs and "ERROR" in all error outputs, there is no need for developers to
include either of these words or anything similar in their warning and error
messages.  It's important that all log and debug messages be chosen to allow for
users to filter out all warning or error messages correctly without
accidentally including general or debug messages in their filtered output.

.. todo::

    Include link to examples in Jupyter book once that exists.
