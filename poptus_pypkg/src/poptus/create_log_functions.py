import functools

from ._constants import (
    LOG_LEVEL_DEFAULT,
    LOG_LEVEL_MIN_DEBUG,
    LOG_LEVEL_MAX,
    POPTUS_LOG_TAG
)
from .AbstractLogger import AbstractLogger
from .StandardLogger import StandardLogger


# ----- CREATE DEDICATED LOG FUNCTIONS
# Boiler plate log function helpers that are used as the building blocks for
# constructing dedicated log functions.  There should be no need to use these
# directly.
def _log(msg, logger, caller):
    logger.log(caller, msg, LOG_LEVEL_DEFAULT)


def _log_debug(msg, debug_level, logger, caller):
    # Since these functions are used by method developers rather than users, we
    # can keep the error checking minimal and light.  If method developers use a
    # bad level, they should find out immediately and easily.
    assert LOG_LEVEL_MIN_DEBUG <= debug_level <= LOG_LEVEL_MAX
    logger.log(caller, msg, debug_level)


def _warn(msg, logger, caller):
    logger.warn(caller, msg)


def _log_and_abort(my_exception, msg, logger, caller):
    logger.error(caller, msg)
    raise my_exception(msg)


def create_log_functions(logger, caller):
    """
    Create a set of simple functions that a method can use for logging general
    information, debug information, warnings, and errors.

    :param logger: Concrete logger object derived from
        :py:class:`AbstractLogger` to be used for logging.  Typically this will
        be created with :py:func:`create_logger`.
    :param caller: Name of element performing the logging.  Depending on the
        logger, this name could appear in each log entry to identify the source
        of the message
    :return: (log, log_debug, warn, log_and_abort) logging functions where

        * ``log(msg)`` logs the given general message at level
          ``LOG_LEVEL_DEFAULT``
        * ``log_debug(msg, level)`` logs the given debug message at the given
          debug level, which must be between ``LOG_LEVEL_MIN_DEBUG`` and
          ``LOG_LEVEL_MAX`` inclusive
        * ``warn(msg)`` logs the given warning message
        * ``log_and_abort(*Error, msg)`` logs the given error message and then
          raises an exception of the given type (|eg| ``ValueError``,
          ``TypeError``)
    """
    if not isinstance(logger, AbstractLogger):
        msg = "Invalid logger type"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise TypeError(msg)
    elif not isinstance(caller, str):
        msg = f"Given logger caller is not a string ({caller})"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise TypeError(msg)
    elif caller == "":
        msg = "Given logger caller is an empty string"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise ValueError(msg)

    log_fcn = functools.partial(_log, logger=logger, caller=caller)
    debug_fcn = functools.partial(_log_debug, logger=logger, caller=caller)
    warn_fcn = functools.partial(_warn, logger=logger, caller=caller)
    error_fcn = functools.partial(_log_and_abort, logger=logger, caller=caller)

    return log_fcn, debug_fcn, warn_fcn, error_fcn
