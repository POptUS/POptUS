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
    def setUp(self):
        self.__tag = "Unittest"

    def testBadLevels(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        bad_levels = [
            None, [poptus.LOG_LEVEL_DEFAULT], 1.1,
            float(poptus.LOG_LEVEL_DEFAULT),
            min(poptus.LOG_LEVELS) - 1,
            max(poptus.LOG_LEVELS) + 1
        ]
        for bad in bad_levels:
            # Confirm that logger is emitting error message to stderr before
            # raising an exception and keep error messages out of test's
            # outputs.
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.StandardLogger(bad)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))

    def testLevel(self):
        logger = poptus.StandardLogger()
        self.assertEqual(poptus.LOG_LEVEL_DEFAULT, logger.level)

        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            self.assertEqual(level, logger.level)

    def testLogErrors(self):
        MSG = "Pointless message that we don't actually want to log"

        # No point in logging with no logging level
        logger = poptus.StandardLogger()
        with self.assertRaises(ValueError):
            logger.log(self.__tag, MSG, poptus.LOG_LEVEL_NONE)

    def testLog(self):
        MSG = "I have something rather important to say"
        EXPECTED = f"[{self.__tag}] {MSG}\n"
        VALID_LEVELS = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        # Confirm nothing written to stdout
        logger = poptus.StandardLogger(poptus.LOG_LEVEL_NONE)
        for level in VALID_LEVELS:
            with redirect_stdout(io.StringIO()) as buffer:
                logger.log(self.__tag, MSG, level)
            self.assertEqual("", buffer.getvalue())

        # Confirm only written to stdout when appropriate
        for level in VALID_LEVELS:
            logger = poptus.StandardLogger(level)

            to_stdout = [e for e in VALID_LEVELS if e <= level]
            for msg_level in to_stdout:
                with redirect_stdout(io.StringIO()) as buffer:
                    logger.log(self.__tag, MSG, msg_level)
                self.assertEqual(EXPECTED, buffer.getvalue())

            skipped = [e for e in VALID_LEVELS if e > level]
            for msg_level in skipped:
                with redirect_stdout(io.StringIO()) as buffer:
                    logger.log(self.__tag, MSG, msg_level)
                self.assertEqual("", buffer.getvalue())

    def testWarn(self):
        MSG = "I am a warning message.  Take heed!"
        EXPECTED = f"[{self.__tag}] WARNING - {MSG}\n"

        # These should emit warning regardless of level to stdout
        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            with redirect_stdout(io.StringIO()) as buffer:
                logger.warn(self.__tag, MSG)
            self.assertEqual(EXPECTED, buffer.getvalue())

    def testError(self):
        MSG = "Something unthinkably horrible has occurred."
        EXPECTED = f"[{self.__tag}] ERROR - {MSG}\n"

        # These should emit error regardless of level to stderr
        for level in poptus.LOG_LEVELS:
            logger = poptus.StandardLogger(level)
            with redirect_stderr(io.StringIO()) as buffer:
                logger.error(self.__tag, MSG)
            self.assertEqual(EXPECTED, buffer.getvalue())
