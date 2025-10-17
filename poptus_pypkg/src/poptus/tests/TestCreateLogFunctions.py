"""
Automatic unittest of the create_log_functions function
"""

import io
import unittest

from contextlib import (
    redirect_stdout, redirect_stderr
)

import poptus


class TestCreateLogFunctions(unittest.TestCase):
    # Since all concrete loggers are tested elsewhere and log functions are
    # created identically regardless of the given logger's type, we assume that
    # it's sufficient to test each generated log function using just the
    # stdout/err logger.
    #
    # All tests should suppress writing to stdout/err, but check content of
    # suppressed messages where useful.

    def setUp(self):
        self.__valid_levels = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        self.__tag = "Unittest"
        self.__error_start = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Confirm good arguments
        self.__good_tag = self.__tag
        self.__good_logger = poptus.StandardLogger()
        log, log_debug, warn, log_and_abort = \
            poptus.create_log_functions(self.__good_logger, self.__good_tag)
        self.assertTrue(callable(log))
        self.assertTrue(callable(log_debug))
        self.assertTrue(callable(warn))
        self.assertTrue(callable(log_and_abort))

        # Include good tag in containers
        self.__bad_tags = [
            None,
            1, 1.1,
            [], [self.__good_tag],
            set(), {self.__good_tag},
            {}, {"Tag": self.__good_tag}
        ]
        # Include good logger in containers
        self.__bad_loggers = [
            None,
            1, 1.1,
            "", "Logger",
            [], [self.__good_logger],
            set(), {self.__good_logger},
            {}, {"Logger": self.__good_logger}
        ]

    def testBadLogger(self):
        for bad in self.__bad_loggers:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_log_functions(bad, self.__good_tag)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testBadCaller(self):
        for bad in self.__bad_tags:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_log_functions(self.__good_logger, bad)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_log_functions(self.__good_logger, "")
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testLogFunction(self):
        MSG = "I have something rather important to say"
        EXPECTED_MSG = f"[{self.__tag}] {MSG}\n"

        # Check no logging explicitly
        logger = poptus.StandardLogger(poptus.LOG_LEVEL_NONE)
        log, _, _, _ = poptus.create_log_functions(logger, self.__tag)

        self.assertTrue(callable(log))

        with redirect_stdout(io.StringIO()) as buffer:
            log(MSG)
        self.assertEqual("", buffer.getvalue())

        for level in self.__valid_levels:
            logger = poptus.StandardLogger(level)
            log, _, _, _ = poptus.create_log_functions(logger, self.__tag)

            self.assertTrue(callable(log))

            with redirect_stdout(io.StringIO()) as buffer:
                log(MSG)
            self.assertEqual(EXPECTED_MSG, buffer.getvalue())

    def testLogDebugFunction(self):
        MSG = "Apparently something has gone wrong..."
        EXPECTED_MSG = f"[{self.__tag}] {MSG}\n"
        MAX_DEBUG_LEVEL = poptus.LOG_LEVEL_MAX - poptus.LOG_LEVEL_MIN_DEBUG
        DEBUG_LEVELS = range(0, MAX_DEBUG_LEVEL + 1)

        # Check no logging explicitly
        for level in {poptus.LOG_LEVEL_NONE, poptus.LOG_LEVEL_DEFAULT}:
            logger = poptus.StandardLogger(level)
            _, log_debug, _, _ = poptus.create_log_functions(logger, self.__tag)

            self.assertTrue(callable(log_debug))
            with self.assertRaises(AssertionError):
                log_debug(MSG, -1)
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    log_debug(MSG, MAX_DEBUG_LEVEL + 1)
            # print(level, buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

            for msg_level in DEBUG_LEVELS:
                with redirect_stdout(io.StringIO()) as buffer:
                    log_debug(MSG, msg_level)
                self.assertEqual("", buffer.getvalue())

        for level in DEBUG_LEVELS:
            logger = poptus.StandardLogger(level + poptus.LOG_LEVEL_MIN_DEBUG)
            _, log_debug, _, _ = \
                poptus.create_log_functions(logger, self.__tag)

            self.assertTrue(callable(log_debug))
            with self.assertRaises(AssertionError):
                log_debug(MSG, -1)
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    log_debug(MSG, MAX_DEBUG_LEVEL + 1)
            # print(level, buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

            to_stdout = [e for e in DEBUG_LEVELS if e <= level]
            for msg_level in to_stdout:
                with redirect_stdout(io.StringIO()) as buffer:
                    log_debug(MSG, msg_level)
                # print(level, msg_level, buffer.getvalue())
                self.assertEqual(EXPECTED_MSG, buffer.getvalue())

            skipped = [e for e in DEBUG_LEVELS if e > level]
            for msg_level in skipped:
                with redirect_stdout(io.StringIO()) as buffer:
                    log_debug(MSG, msg_level)
                self.assertEqual("", buffer.getvalue())

    def testWarnFunction(self):
        MSG = "Tread lightly.  For all is not well."
        EXPECTED_MSG = f"[{self.__tag}] WARNING - {MSG}\n"

        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            _, _, warn, _ = poptus.create_log_functions(logger, self.__tag)

            self.assertTrue(callable(warn))

            with redirect_stdout(io.StringIO()) as buffer:
                warn(MSG)
            # print(level, buffer.getvalue())
            self.assertEqual(EXPECTED_MSG, buffer.getvalue())

    def testLogAndAbortFunction(self):
        MSG = "Goodness gracious!  What have you done?!"
        EXPECTED_MSG = f"[{self.__tag}] ERROR - {MSG}\n"
        EXCEPTIONS_ALL = {
            ValueError, TypeError, RuntimeError,
            AssertionError, NotImplementedError
        }

        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            _, _, _, log_and_abort = \
                poptus.create_log_functions(logger, self.__tag)

            self.assertTrue(callable(log_and_abort))

            for excpt in EXCEPTIONS_ALL:
                with redirect_stderr(io.StringIO()) as buffer:
                    with self.assertRaises(excpt):
                        log_and_abort(excpt, MSG)
                # print(level, buffer.getvalue())
                self.assertEqual(EXPECTED_MSG, buffer.getvalue())
