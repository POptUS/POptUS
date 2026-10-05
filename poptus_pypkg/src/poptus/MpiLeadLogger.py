import sys

from ._constants import (
    LOG_LEVELS, LOG_LEVEL_NONE, LOG_LEVEL_DEFAULT
)
from .AbstractLogger import AbstractLogger


class MpiLeadLogger(AbstractLogger):
    def __init__(self, level=LOG_LEVEL_DEFAULT):
        """
        A concrete |poptus| logger class that implements an MPI-aware variant of
        the :py:class:`poptus.StandardLogger` for general logging in MPI-based
        applications |via| the MPI process that calling code designates as the
        lead logging process (See :py:func:`poptus.create_logger`).

        :param level: Verbosity level of the logger
        """
        # This error checks level
        super().__init__(level)

        # LOG_LEVEL_NONE is not an acceptable message level for general logging
        # as per the documentation in AbstractLogger.
        self.__valid = set(LOG_LEVELS).difference({LOG_LEVEL_NONE})

    def log(self, caller, msg, level):
        """
        Print the given message to ``stdout`` if the logger's verbosity level
        is greater than or equal to the given message's level.

        Presently, this implementation flushes stdout on each message to ensure
        reasonably good chronological ordering of MPI messages.

        :param caller: Name of calling code for inclusion in actual logged
            message
        :param msg: Message to potentially log
        :param level: Message's log level
        """
        # Since the use of these functions is setup by developers rather than
        # users, we can keep the error checking minimal and light.  If
        # developers use a bad level, they should find out immediately and
        # easily.
        assert level in self.__valid

        if self.level >= level:
            sys.stdout.write(f"[{caller}] {msg}\n")
            sys.stdout.flush()

    def warn(self, caller, msg):
        """
        Print the given message to ``stdout`` in such a way that it is clear
        that it is transmitting a warning message to users.  This is printed
        regardless of the logger's verbosity level.

        Presently, this implementation flushes stdout on each message to ensure
        reasonably good chronological ordering of MPI messages.

        :param caller: Name of calling code for inclusion in actual logged
            warning
        :param msg: Warning message to log
        """
        sys.stdout.write(f"[{caller}] WARNING - {msg}\n")
        sys.stdout.flush()

    def error(self, caller, msg):
        """
        Print the given message to ``stderr`` in such a way that it is clear
        that it is transmitting an error message to users.  This is printed
        regardless of the logger's verbosity level.

        :param caller: Name of calling code for inclusion in actual logged
            error
        :param msg: Error message to log
        """
        sys.stderr.write(f"[{caller}] ERROR - {msg}\n")
        sys.stderr.flush()
