import os
import sys

from pathlib import Path

from ._constants import (
    LOG_LEVELS, LOG_LEVEL_NONE, LOG_LEVEL_DEFAULT,
    POPTUS_LOG_TAG
)
from .AbstractLogger import AbstractLogger
from .StandardLogger import StandardLogger


class FileLogger(AbstractLogger):
    def __init__(self, filename, overwrite, level=LOG_LEVEL_DEFAULT):
        """
        A concrete |poptus| logger class that writes all log, warning, and error
        messages to the given file.  Error messages are also written to standard
        error.

        :param level: Verbosity level of the logger
        :param filename: Name and path of file to write to
        :param overwrite: If a file with the given name already exists, then it
            is overwritten if ``True`` or an error is raised if ``False``.
        """
        def warn(msg):
            StandardLogger(LOG_LEVEL_NONE).warn(POPTUS_LOG_TAG, msg)

        def log_and_abort(my_exception, msg):
            StandardLogger(LOG_LEVEL_NONE).error(POPTUS_LOG_TAG, msg)
            raise my_exception(msg)

        # This error checks level
        super().__init__(level)

        if not isinstance(filename, (str, Path)):
            log_and_abort(TypeError, f"{filename} is not a string or Path")
        elif isinstance(filename, str) and (filename == ""):
            log_and_abort(ValueError, "Empty filename string given")
        elif not isinstance(overwrite, bool):
            log_and_abort(TypeError, f"overwrite is not a bool ({overwrite})")

        self.__filename = Path(filename).resolve()
        if self.__filename.exists():
            if not overwrite:
                msg = f"{self.__filename} already exists"
                log_and_abort(RuntimeError, msg)
            elif not self.__filename.is_file():
                msg = "Cannot overwrite {} since it is not a file"
                log_and_abort(RuntimeError, msg.format(self.__filename))
            else:
                warn(f"Overwriting {self.__filename}")
                os.remove(self.__filename)

        # LOG_LEVEL_NONE is not an acceptable message level for general logging
        # as per the documentation in AbstractLogger.
        self.__valid = set(LOG_LEVELS).difference({LOG_LEVEL_NONE})

    @property
    def filename(self):
        """
        :return: Name including path of file to which log information is written
        """
        return self.__filename

    def log(self, caller, msg, level):
        """
        Write the given message to file if the logger's verbosity level is
        greater than or equal to the given message's level.

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
            with open(self.__filename, "a") as fptr:
                fptr.write(f"[{caller}] {msg}\n")

    def warn(self, caller, msg):
        """
        Write the given message to file in such a way that it is clear that it
        is transmitting a warning message to users.  This is printed regardless
        of the logger's verbosity level.

        :param caller: Name of calling code for inclusion in actual logged
            warning
        :param msg: Warning message to log
        """
        with open(self.__filename, "a") as fptr:
            fptr.write(f"[{caller}] WARNING - {msg}\n")

    def error(self, caller, msg):
        """
        Print the given message to ``stderr`` and write to file in such a way
        that it is clear that it is transmitting an error message to users.
        This is printed regardless of the logger's verbosity level.

        :param caller: Name of calling code for inclusion in actual logged
            error
        :param msg: Error message to log
        """
        sys.stderr.write(f"[{caller}] ERROR - {msg}\n")
        sys.stderr.flush()

        with open(self.__filename, "a") as fptr:
            fptr.write(f"[{caller}] ERROR - {msg}\n")
