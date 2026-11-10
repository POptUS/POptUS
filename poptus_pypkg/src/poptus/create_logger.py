from ._constants import (
    LOG_LEVEL_DEFAULT,
    LOG_LEVEL_KEY, LOG_FILENAME_KEY, LOG_OVERWRITE_KEY,
    POPTUS_LOG_TAG
)
from .StandardLogger import StandardLogger
from .FileLogger import FileLogger
from .MpiLeadLogger import MpiLeadLogger
from .MpiWorkerLogger import MpiWorkerLogger


def create_logger(configuration=None, rank=None, is_lead=False):
    """
    Please refer to the general logging documentation in the User Guide for
    information on configuring |poptus| loggers.

    :param configuration: ``None`` or the full logger configuration specified as
        a ``dict``.
    :param rank: Nonnegative rank of MPI process requesting logger; ``None``, if
        the logger will not be used in an MPI application.
    :param is_lead: Set to ``True`` if the process creating the logger should be
        considered as the lead MPI process in terms of logging.  Typically one
        and only one MPI process is declared the lead logger process.  This is
        ignored if ``rank`` is ``None``.
    :return: If ``configuration`` is ``None``, then a standard ouput/standard
        error logger with the ``LOG_LEVEL_DEFAULT`` verbosity level is
        returned.  Otherwise, a logger built with the provided configuration is
        returned.
    """
    STD_CFG_KEYS = {LOG_LEVEL_KEY}
    FILE_CFG_KEYS = {
        LOG_LEVEL_KEY,
        LOG_FILENAME_KEY,
        LOG_OVERWRITE_KEY
    }

    if configuration is None:
        configuration = {LOG_LEVEL_KEY: LOG_LEVEL_DEFAULT}

    if not isinstance(configuration, dict):
        msg = "Given logger configuration is not a dict"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise TypeError(msg)
    elif LOG_LEVEL_KEY not in configuration:
        msg = f"{LOG_LEVEL_KEY} logger configuration not provided"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise ValueError(msg)

    if not isinstance(is_lead, bool):
        msg = f"is_lead is not a boolean ({is_lead})"
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise TypeError(msg)

    # Assume that logger classes are error checking their arguments
    level = configuration[LOG_LEVEL_KEY]

    # ----- MPI-AWARE LOGGING
    if rank is not None:
        if LOG_FILENAME_KEY in configuration:
            msg = "No logging to files in MPI-based applications"
            StandardLogger().error(POPTUS_LOG_TAG, msg)
            raise NotImplementedError(msg)

        if set(configuration) != STD_CFG_KEYS:
            msg = "Invalid configuration keys for MPI loggers ({})"
            msg = msg.format(set(configuration))
            StandardLogger().error(POPTUS_LOG_TAG, msg)
            raise ValueError(msg)

        if is_lead:
            return MpiLeadLogger(level)

        return MpiWorkerLogger(rank, level)

    # ----- NON-MPI APPLICATIONS
    assert rank is None
    if LOG_FILENAME_KEY in configuration:
        if set(configuration) != FILE_CFG_KEYS:
            msg = "Invalid configuration keys for file logger ({})"
            msg = msg.format(set(configuration))
            StandardLogger().error(POPTUS_LOG_TAG, msg)
            raise ValueError(msg)

        return FileLogger(
            configuration[LOG_FILENAME_KEY],
            configuration[LOG_OVERWRITE_KEY],
            level
        )
    elif set(configuration) != STD_CFG_KEYS:
        msg = "Invalid configuration keys for standard out/err  logger ({})"
        msg = msg.format(set(configuration))
        StandardLogger().error(POPTUS_LOG_TAG, msg)
        raise ValueError(msg)

    return StandardLogger(level)
