import sys
import numbers

from ._constants import (
    LOG_LEVELS, LOG_LEVEL_NONE, LOG_LEVEL_MIN_DEBUG,
    POPTUS_LOG_TAG
)
from .AbstractLogger import AbstractLogger


class MpiWorkerLogger(AbstractLogger):
    def __init__(self, rank, level):
        """
        A concrete |poptus| logger class that implements an MPI-aware variant of
        the :py:class:`poptus.StandardLogger` for limited logging in MPI-based
        applications |via| MPI processes that calling code designates as
        worker processes (See :py:func:`poptus.create_logger`).  This class
        ignores all requests to log general information at ``LOG_LEVEL_DEFAULT``
        regardless of the level given at instantiation.

        This design allows for writing log commands in MPI-based code without
        having to wrap each log command in a check of rank so that only the lead
        process logs general information.  It still allows for each MPI process
        to log its debug information and for all processes to report warnings
        and errors.

        :param rank: Nonnegative MPI rank of the calling process.  This is used
            to compose the tag of the logger.
        :param level: Verbosity level of the logger.
        """
        # This error checks level
        super().__init__(level)

        # To avoid requiring mpi4py as an explicit dependence of this package,
        # we don't get the COMM size here to error check the rank further.
        # Rather, we perform these sanity checks and expect users to supply
        # ranks correctly otherwise.
        self.__tag = POPTUS_LOG_TAG
        if not isinstance(rank, numbers.Integral):
            msg = f"MPI process rank is not an integer ({rank})"
            self.error(None, msg)
            raise TypeError(msg)
        elif rank < 0:
            msg = f"Negative MPI process rank ({rank})"
            self.error(None, msg)
            raise ValueError(msg)
        self.__tag = f"Rank {rank}"

        # LOG_LEVEL_NONE is not an acceptable message level for general logging
        # as per the documentation in AbstractLogger.
        self.__valid = set(LOG_LEVELS).difference({LOG_LEVEL_NONE})

    def log(self, _, msg, level):
        """
        Print the given message to ``stdout`` if the message's level is greater
        than ``LOG_LEVEL_MIN_DEBUG`` and the logger's verbosity level is greater
        than or equal to the given message's level.

        :param caller: Ignored
        :param msg: Debug message to potentially log
        :param level: Message's log level
        """
        # Since the use of these functions is setup by developers rather than
        # users, we can keep the error checking minimal and light.  If
        # developers use a bad level, they should find out immediately and
        # easily.
        assert level in self.__valid

        if (level >= LOG_LEVEL_MIN_DEBUG) and (self.level >= level):
            sys.stdout.write(f"[{self.__tag}] {msg}\n")
            sys.stdout.flush()

    def warn(self, _, msg):
        """
        Print the given message to ``stdout`` in such a way that it is clear
        that it is transmitting a warning message to users.  This is printed
        regardless of the logger's verbosity level.

        :param caller: Ignored
        :param msg: Warning message to log
        """
        sys.stdout.write(f"[{self.__tag}] WARNING - {msg}\n")
        sys.stdout.flush()

    def error(self, _, msg):
        """
        Print the given message to ``stderr`` in such a way that it is clear
        that it is transmitting an error message to users.  This is printed
        regardless of the logger's verbosity level.

        :param caller: Ignored
        :param msg: Error message to log
        """
        sys.stderr.write(f"[{self.__tag}] ERROR - {msg}\n")
        sys.stderr.flush()
