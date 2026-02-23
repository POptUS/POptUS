import sys

from ._constants import LOG_LEVEL_MIN_DEBUG
from .AbstractLogger import AbstractLogger


class MpiWorkerLogger(AbstractLogger):
    def __init__(self, rank, level):
        """
        A concrete |poptus| logger class that ignores all requests to log
        general information at LOG_LEVEL_DEFAULT regardless of the level given
        at instantiation.  Typically, all MPI worker processes would use this as
        their logger.

        This allows for writing log commands in MPI-based code without having to
        wrap each log command in a check of rank so that only the lead process
        logs general information.  It still allows for each MPI process to log
        its debug information and for all processes to report warnings and
        errors.

        :param rank: MPI rank of the process.  This is used to compose the
            tag of the logger.
        :param level: Verbosity level of the logger.
        """
        # This error checks level
        super().__init__(level)

        self.__tag = f"Rank {rank}"

    def log(self, _, msg, level):
        """
        Print the given message to ``stdout`` if the message's level is greater
        than LOG_LEVEL_MIN_DEBUG and the logger's verbosity level is greater
        than or equal to the given message's level.

        :param caller: Ignored
        :param msg: Debug message to potentially log
        :param level: Message's log level
        """
        if (level >= LOG_LEVEL_MIN_DEBUG) and (self.level >= level):
            sys.stdout.write(f"[{self.__tag}] {msg}\n")

    def warn(self, _, msg):
        """
        Print the given message to ``stdout`` in such a way that it is clear
        that it is transmitting a warning message to users.  This is printed
        regardless of the logger's verbosity level.

        :param caller: Ignored
        :param msg: Warning message to log
        """
        sys.stdout.write(f"[{self.__tag}] WARNING - {msg}\n")

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
