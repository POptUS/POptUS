"""
Automatic unittest of the create_logger function
"""

import io
import unittest

from contextlib import redirect_stderr

import poptus


class TestCreateLogger(unittest.TestCase):
    def testCreateDefault(self):
        logger = poptus.create_logger()
        self.assertTrue(isinstance(logger, poptus.StandardLogger))
        self.assertEqual(poptus.LOG_LEVEL_DEFAULT, logger.level)

    def testBadConfigurationType(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Suppress but check error messages written to stderr
        bad_configs = [
            1, 1.1, [], [1.1], set(), {1.1}
        ]
        for config in bad_configs:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_logger(config)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))

    def testBadConfigurations(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Suppress but check error messages written to stderr

        # No level specification
        bad_configs = [
            {},
            {"something": poptus.LOG_LEVEL_DEFAULT},
            {poptus._constants.LOG_FILENAME_KEY: ""}
        ]
        for config in bad_configs:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_logger(config)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))

    def testCreateStandardLogger(self):
        VALID_LEVELS = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        for level in VALID_LEVELS:
            config = {
                poptus._constants.LOG_LEVEL_KEY: level
            }
            logger = poptus.create_logger(config)
            self.assertTrue(isinstance(logger, poptus.StandardLogger))
            self.assertEqual(level, logger.level)

    def testCreateFileLogger(self):
        FILENAME = "not_important.log"
        VALID_LEVELS = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        for level in VALID_LEVELS:
            config = {
                poptus._constants.LOG_LEVEL_KEY: level,
                poptus._constants.LOG_FILENAME_KEY: FILENAME
            }
            with self.assertRaises(NotImplementedError):
                poptus.create_logger(config)
