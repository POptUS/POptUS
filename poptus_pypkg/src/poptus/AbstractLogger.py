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
        communicate to users all general, warning, and error messages.  In this
        way, this package helps implement and enforce a common, uniform logging
        interface across the universe.

        Note that this requirement includes all command line tools thaat might
        be called by users.  For instance, these tools should log errors
        through a logger rather than printing to stdout/stderr themselves.

        :param level: Verbosity level of the logger
        """
        super().__init__()

        self.__level = level
        if (not isinstance(self.__level, Integral)) or \
                (self.__level not in LOG_LEVELS):
            # Calling code does not have access to the logger for printing the
            # error message.  Log it on their behalf.
            msg = f"Invalid code generation logging level ({self.__level})"
            self.error(POPTUS_LOG_TAG, msg)
            raise ValueError(msg)

    @property
    def level(self):
        """
        :return: All log messages with a level less than or equal to this value
            will be logged.  Warning and errors are logged regardless of this
            value.
        """
        return self.__level

    @abc.abstractmethod
    def log(self, caller, msg, min_level):
        """
        Log the given message if the logger's verbosity level is greater than
        or equal to the given logging threshold level.  The actual, final
        logged message, which includes the message provided by the caller,
        should not given any indication that the message indicates a warning or
        an error.

        It is a logical error for the given level to be LOG_LEVELS_NONE.
        Concrete loggers derived from this class are responsible for enforcing
        this.

        :param caller: Name of calling code so that concrete logger can include
            this in actual logged message if so desired
        :param msg: Message to potentially log
        :param min_level: Message's log level
        """
        ...

    @abc.abstractmethod
    def warn(self, caller, msg):
        """
        Log given message in such a way that it is clear that it is
        transmitting a warning message to users.  This is printed regardless of
        the logger's verbosity level.

        :param caller: Name of calling code so that concrete logger can include
            this in actual logged message if so desired
        :param msg: Warning message to log
        """
        ...

    @abc.abstractmethod
    def error(self, caller, msg):
        """
        Log given message in such a way that it is clear that it is
        transmitting an error message to users.  This is printed regardless of
        the logger's verbosity level.

        :param caller: Name of calling code so that concrete logger can include
            this in actual logged message if so desired
        :param msg: Error message to log
        """
        ...
