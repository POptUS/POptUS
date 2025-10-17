import sys

from ._constants import (
    LOG_LEVELS, LOG_LEVEL_NONE, LOG_LEVEL_DEFAULT
)
from .AbstractLogger import AbstractLogger


class StandardLogger(AbstractLogger):
    def __init__(self, level=LOG_LEVEL_DEFAULT):
        """
        A concrete |poptus| logger class that is "standard" in the sense that
        many |poptus| applications and users might choose to use this directly
        and because logging is done using standard output and error.

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

    def warn(self, caller, msg):
        """
        Print the given message to ``stdout`` in such a way that it is clear
        that it is transmitting a warning message to users.  This is printed
        regardless of the logger's verbosity level.

        :param caller: Name of calling code for inclusion in actual logged
            warning
        :param msg: Warning message to log
        """
        sys.stdout.write(f"[{caller}] WARNING - {msg}\n")

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
