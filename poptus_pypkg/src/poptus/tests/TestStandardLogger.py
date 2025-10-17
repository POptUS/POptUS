"""
Automatic unittest of the StandardLogger class
"""

import io
import unittest

from contextlib import (
    redirect_stdout, redirect_stderr
)

import poptus


class TestStandardLogger(unittest.TestCase):
    # All tests should suppress writing to stdout/err, but check content of
    # suppressed messages where useful.

    def setUp(self):
        self.__valid_levels = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        self.__tag = "Unittest"
        self.__error_start = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Confirm good configurations
        self.__good_level = poptus.LOG_LEVEL_DEFAULT
        poptus.StandardLogger(self.__good_level)

        # Include valid levels in containers
        self.__bad_levels = [
            None,
            1.1, float(self.__good_level),
            "", str(self.__good_level),
            [], [self.__good_level],
            set(), {self.__good_level},
            min(poptus.LOG_LEVELS) - 1,
            max(poptus.LOG_LEVELS) + 1
        ]

    def testBadLevels(self):
        for bad in self.__bad_levels:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.StandardLogger(bad)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testLevel(self):
        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            self.assertEqual(level, logger.level)

    def testDefaultLevel(self):
        logger = poptus.StandardLogger()
        self.assertEqual(poptus.LOG_LEVEL_DEFAULT, logger.level)

    def testLogErrors(self):
        MSG = "Pointless message that we don't actually want to log"

        logger = poptus.StandardLogger(poptus.LOG_LEVEL_DEFAULT)
        with self.assertRaises(AssertionError):
            logger.log(self.__tag, MSG, poptus.LOG_LEVEL_NONE)

    def testLog(self):
        MSG = "I have something rather important to say"
        EXPECTED_MSG = f"[{self.__tag}] {MSG}\n"

        # Explicitly check no logging
        logger = poptus.StandardLogger(poptus.LOG_LEVEL_NONE)
        for level in self.__valid_levels:
            with redirect_stdout(io.StringIO()) as buffer:
                logger.log(self.__tag, MSG, level)
            self.assertEqual("", buffer.getvalue())

        for level in self.__valid_levels:
            logger = poptus.StandardLogger(level)

            to_stdout = [e for e in self.__valid_levels if e <= level]
            for msg_level in to_stdout:
                with redirect_stdout(io.StringIO()) as buffer:
                    logger.log(self.__tag, MSG, msg_level)
                # print(level, msg_level, buffer.getvalue())
                self.assertEqual(EXPECTED_MSG, buffer.getvalue())

            skipped = [e for e in self.__valid_levels if e > level]
            for msg_level in skipped:
                with redirect_stdout(io.StringIO()) as buffer:
                    logger.log(self.__tag, MSG, msg_level)
                self.assertEqual("", buffer.getvalue())

    def testWarn(self):
        MSG = "I am a warning message.  Take heed!"
        EXPECTED_MSG = f"[{self.__tag}] WARNING - {MSG}\n"

        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            with redirect_stdout(io.StringIO()) as buffer:
                logger.warn(self.__tag, MSG)
            self.assertEqual(EXPECTED_MSG, buffer.getvalue())

    def testError(self):
        MSG = "Something unthinkably horrible has occurred."
        EXPECTED_MSG = f"[{self.__tag}] ERROR - {MSG}\n"

        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            with redirect_stderr(io.StringIO()) as buffer:
                logger.error(self.__tag, MSG)
            self.assertEqual(EXPECTED_MSG, buffer.getvalue())
