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
    def setUp(self):
        self.__tag = "Unittest"
        self.__log_msg = "I have something rather important to say"
        self.__warn_msg = "Tread lightly.  For all is not as expected."
        self.__err_msg = "Goodness gracious!  What have you done?"

    def testBadLogger(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Confirm good arguments
        good_tag = self.__tag
        poptus.create_log_functions(poptus.StandardLogger(), good_tag)

        bad_loggers = [
            None,
            "", "not a logger",
            1, 1.1,
            [], [poptus.StandardLogger()], [1.1],
            set(), {poptus.StandardLogger()}, {1.1},
            {}, {"a": poptus.StandardLogger()}
        ]
        for bad in bad_loggers:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_log_functions(bad, good_tag)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))

    def testBadCaller(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        good_logger = poptus.StandardLogger()

        # Confirm good arguments
        poptus.create_log_functions(good_logger, self.__tag)

        bad_tags = [
            None,
            1, 1.1,
            [], [poptus.StandardLogger()], [1.1],
            set(), {poptus.StandardLogger()}, {1.1},
            {}, {"a": poptus.StandardLogger()}
        ]
        for bad in bad_tags:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_log_functions(good_logger, bad)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))

        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_log_functions(good_logger, "")
        self.assertTrue(buffer.getvalue().startswith(MSG_START))

    def testStandardLogger(self):
        # Since each concrete logger class is individually tested, it should be
        # sufficient to just check the log functions with one type of logger.
        VALID_LEVELS = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )
        MAX_DEBUG_LEVEL = poptus.LOG_LEVEL_MAX - poptus.LOG_LEVEL_MIN_DEBUG
        DEBUG_LEVELS = range(0, MAX_DEBUG_LEVEL + 1)
        EXPECTED_LOG = f"[{self.__tag}] {self.__log_msg}\n"
        EXPECTED_WARN = f"[{self.__tag}] WARNING - {self.__warn_msg}\n"
        EXPECTED_ERROR = f"[{self.__tag}] ERROR - {self.__err_msg}\n"

        # Check no logging specifically
        logger = poptus.StandardLogger(poptus.LOG_LEVEL_NONE)
        log, log_debug, warn, log_and_abort = \
            poptus.create_log_functions(logger, self.__tag)

        self.assertTrue(callable(log))
        self.assertTrue(callable(log_debug))
        self.assertTrue(callable(warn))
        self.assertTrue(callable(log_and_abort))
        with self.assertRaises(AssertionError):
            log_debug(self.__log_msg, -1)
        with self.assertRaises(ValueError):
            log_debug(self.__log_msg, MAX_DEBUG_LEVEL + 1)

        # General info
        with redirect_stdout(io.StringIO()) as buffer:
            log(self.__log_msg)
        self.assertEqual("", buffer.getvalue())

        # Debugging
        for msg_level in DEBUG_LEVELS:
            with redirect_stdout(io.StringIO()) as buffer:
                log_debug(self.__log_msg, msg_level)
            self.assertEqual("", buffer.getvalue())

        # Warnings - always logged
        with redirect_stdout(io.StringIO()) as buffer:
            warn(self.__warn_msg)
        self.assertEqual(EXPECTED_WARN, buffer.getvalue())

        # Errors - always logged
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                log_and_abort(ValueError, self.__err_msg)
            self.assertEqual(EXPECTED_ERROR, buffer.getvalue())

        # Check for some logging
        for level in VALID_LEVELS:
            logger = poptus.StandardLogger(level)
            log, log_debug, warn, log_and_abort = \
                poptus.create_log_functions(logger, self.__tag)

            self.assertTrue(callable(log))
            self.assertTrue(callable(log_debug))
            self.assertTrue(callable(warn))
            self.assertTrue(callable(log_and_abort))
            with self.assertRaises(AssertionError):
                log_debug(self.__log_msg, -1)
            with self.assertRaises(ValueError):
                log_debug(self.__log_msg, MAX_DEBUG_LEVEL + 1)

            # General info - always logged
            with redirect_stdout(io.StringIO()) as buffer:
                log(self.__log_msg)
            self.assertEqual(EXPECTED_LOG, buffer.getvalue())

            # Debugging
            to_stdout = [e for e in DEBUG_LEVELS
                         if e + poptus.LOG_LEVEL_MIN_DEBUG <= level]
            for msg_level in to_stdout:
                with redirect_stdout(io.StringIO()) as buffer:
                    log_debug(self.__log_msg, msg_level)
                self.assertEqual(EXPECTED_LOG, buffer.getvalue())

            skipped = [e for e in DEBUG_LEVELS
                       if e + poptus.LOG_LEVEL_MIN_DEBUG > level]
            for msg_level in skipped:
                with redirect_stdout(io.StringIO()) as buffer:
                    log_debug(self.__log_msg, msg_level)
                self.assertEqual("", buffer.getvalue())

            # Warnings - always logged
            with redirect_stdout(io.StringIO()) as buffer:
                warn(self.__warn_msg)
            self.assertEqual(EXPECTED_WARN, buffer.getvalue())

            # Errors - always logged
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    log_and_abort(ValueError, self.__err_msg)
                self.assertEqual(EXPECTED_ERROR, buffer.getvalue())
