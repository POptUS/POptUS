import os
import sys

from pathlib import Path

from ._constants import (
    LOG_LEVELS, LOG_LEVEL_NONE,
    POPTUS_LOG_TAG
)
from .AbstractLogger import AbstractLogger
from .StandardLogger import StandardLogger


class FileLogger(AbstractLogger):
    def __init__(self, level, filename, overwrite):
        """
        A concrete |poptus| logger class that writes all log, warning, and error
        messages to the given file.  Error messages are also written to standard
        error.

        .. todo::
            * Can we set this up so that the file is always open but gets
              closed automatically if an exception is raised?  It seems like if
              we want this, it would have to be managed differently from the
              Archiver since its use would depend more on what calling code is
              doing.

        :param level: Verbosity level of the logger
        :param filename: Name and path of file to write to
        :param overwrite: Allow pre-existing file to be overwritten
        """
        def warn(msg):
            StandardLogger(LOG_LEVEL_NONE).warn(POPTUS_LOG_TAG, msg)

        def log_and_abort(excpt, msg):
            StandardLogger(LOG_LEVEL_NONE).error(POPTUS_LOG_TAG, msg)
            raise excpt(msg)

        if not isinstance(filename, (str, Path)):
            log_and_abort(TypeError, f"{filename} is not a string or Path")
        elif isinstance(filename, str) and (filename == ""):
            log_and_abort(ValueError, "Empty filename string given")
        elif not isinstance(overwrite, bool):
            log_and_abort(TypeError, f"overwrite ({overwrite}) is not a bool")

        self.__filename = Path(filename).resolve()
        if self.__filename.exists():
            if not overwrite:
                msg = f"{self.__filename} already exists"
                log_and_abort(RuntimeError, msg)
            elif not self.__filename.is_file():
                msg = "Cannot overwrite {} since it is not a file"
                msg = msg.format(self.__filename)
                log_and_abort(RuntimeError, msg)
            else:
                warn(f"Overwriting {self.__filename}")
                os.remove(self.__filename)

        # Base class might need to call the concrete logger's error function to
        # report errors.  Therefore, setup logger as much as possible first.
        #
        # This error checks level
        super().__init__(level)

        self.__valid = set(LOG_LEVELS).difference({LOG_LEVEL_NONE})

    @property
    def filename(self):
        """
        :return: Name including path of file to which log information is written
        """
        return self.__filename

    def log(self, caller, msg, min_level):
        """
        Write the given message to file if the logger's verbosity level is
        greater than or equal to the given logging threshold level.

        :param caller: Name of calling code for inclusion in actual logged
            message
        :param msg: Message to potentially log
        :param min_level: Message's log level
        """
        if min_level not in self.__valid:
            msg = f"Invalid code generation logging level ({min_level})"
            raise ValueError(msg)

        if self.level >= min_level:
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
