import sys
import abc

from numbers import Integral

from ._constants import (
    LOG_LEVELS,
    POPTUS_LOG_TAG
)


class AbstractLogger(metaclass=abc.ABCMeta):
    def __init__(self, level):
        """
        It is intended that all tools in the |poptus| universe use objects
        instantiated from concrete logger classes derived from this class to
        communicate to users all general, debug, warning, and error messages.
        In this way, this package helps implement and enforce a common, uniform
        logging interface across the universe.

        :param level: Verbosity level of the logger
        """
        super().__init__()

        if (not isinstance(level, Integral)) or (level not in LOG_LEVELS):
            # Do not assume that we can use derived class logging functions yet.
            # Mimic error logging of StandardLogger.
            msg = f"Invalid logging verbosity level ({level})"
            sys.stderr.write(f"[{POPTUS_LOG_TAG}] ERROR - {msg}\n")
            sys.stderr.flush()
            raise ValueError(msg)

        self.__level = level

    @property
    def level(self):
        """
        :return: Logger's verbosity level
        """
        return self.__level

    @abc.abstractmethod
    def log(self, caller, msg, level):
        """
        Log the given message if the logger's verbosity level is greater than or
        equal to the given message's level.  The actual, final logged message,
        which includes the message provided by the caller, should not given any
        indication that the message indicates a warning or an error.

        It is a logical error for the given message level to be
        ``LOG_LEVELS_NONE``.  Concrete loggers derived from this class are
        responsible for enforcing this.

        :param caller: Name of calling code so that concrete logger can include
            this in actual logged message if so desired
        :param msg: Message to potentially log
        :param level: Message's log level
        """
        ...

    @abc.abstractmethod
    def warn(self, caller, msg):
        """
        Log given message in such a way that it is clear that it is transmitting
        a warning message to users.  This is printed regardless of the logger's
        verbosity level.

        :param caller: Name of calling code so that concrete logger can include
            this in actual logged message if so desired
        :param msg: Warning message to log
        """
        ...

    @abc.abstractmethod
    def error(self, caller, msg):
        """
        Log given message in such a way that it is clear that it is transmitting
        an error message to users.  This is printed regardless of the logger's
        verbosity level.

        :param caller: Name of calling code so that concrete logger can include
            this in actual logged message if so desired
        :param msg: Error message to log
        """
        ...
