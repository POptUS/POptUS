from ._constants import (
    LOG_LEVEL_DEFAULT,
    LOG_LEVEL_KEY, LOG_FILENAME_KEY, LOG_OVERWRITE_KEY,
    POPTUS_LOG_TAG
)
from .StandardLogger import StandardLogger
from .FileLogger import FileLogger


def create_logger(configuration=None):
    """
    Please refer to the general logging documentation in the User Guide for
    information on configuring |poptus| loggers.

    :param configuration: ``None`` or the full logger configuration specified as
        a ``dict``.
    :return: If ``configuration`` is ``None``, then a standard ouput/standard
        error logger with the ``LOG_LEVEL_DEFAULT`` verbosity level is
        returned.  Otherwise, a logger built with the provided configuration is
        returned.
    """
    if configuration is None:
        return StandardLogger(LOG_LEVEL_DEFAULT)
    elif not isinstance(configuration, dict):
        msg = "Given logger configuration is not a dict"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise TypeError(msg)
    elif LOG_LEVEL_KEY not in configuration:
        msg = f"{LOG_LEVEL_KEY} logger configuration not provided"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise ValueError(msg)

    # Assume that logger classes are error checking their arguments
    level = configuration[LOG_LEVEL_KEY]

    if LOG_FILENAME_KEY in configuration:
        if LOG_OVERWRITE_KEY not in configuration:
            msg = f"{LOG_OVERWRITE_KEY} logger configuration not provided"
            StandardLogger().error(POPTUS_LOG_TAG, msg)
            raise ValueError(msg)

        return FileLogger(
            level,
            configuration[LOG_FILENAME_KEY],
            configuration[LOG_OVERWRITE_KEY]
        )
    elif LOG_OVERWRITE_KEY in configuration:
        msg = f"{LOG_OVERWRITE_KEY} logger configuration not required"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise ValueError(msg)

    return StandardLogger(level)
