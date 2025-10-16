"""
Automatic unittest of the create_logger function
"""

import io
import unittest

from pathlib import Path
from contextlib import redirect_stderr

import poptus


class TestCreateLogger(unittest.TestCase):
    def setUp(self):
        self.__error_start = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

    def testCreateDefault(self):
        logger = poptus.create_logger()
        self.assertTrue(isinstance(logger, poptus.StandardLogger))
        self.assertEqual(poptus.LOG_LEVEL_DEFAULT, logger.level)

    def testBadConfigurationType(self):
        # Suppress but check error messages written to stderr
        bad_configs = [
            1, 1.1, [], [1.1], set(), {1.1}
        ]
        for config in bad_configs:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_logger(config)
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testBadConfigurations(self):
        # Confirm good config values
        good_filename = Path.cwd().joinpath("test.log")

        good_std_config = {
            poptus._constants.LOG_LEVEL_KEY: poptus.LOG_LEVEL_DEFAULT
        }
        logger = poptus.create_logger(good_std_config)
        self.assertTrue(isinstance(logger, poptus.StandardLogger))

        good_file_config = {
            poptus._constants.LOG_LEVEL_KEY: poptus.LOG_LEVEL_DEFAULT,
            poptus._constants.LOG_FILENAME_KEY: good_filename,
            poptus._constants.LOG_OVERWRITE_KEY: False
        }
        logger = poptus.create_logger(good_file_config)
        self.assertTrue(isinstance(logger, poptus.FileLogger))

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
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Overwrite for standard logger
        bad_config = good_std_config.copy()
        bad_config[poptus._constants.LOG_OVERWRITE_KEY] = True
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad_config)
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Missing overwrite for file logger
        bad_config = good_file_config.copy()
        del bad_config[poptus._constants.LOG_OVERWRITE_KEY]
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad_config)
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

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
        FILENAME = Path.cwd().joinpath("not_important.log")
        VALID_LEVELS = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        for level in VALID_LEVELS:
            config = {
                poptus._constants.LOG_LEVEL_KEY: level,
                poptus._constants.LOG_FILENAME_KEY: FILENAME,
                poptus._constants.LOG_OVERWRITE_KEY: False
            }
            logger = poptus.create_logger(config)
            self.assertTrue(isinstance(logger, poptus.FileLogger))
            self.assertEqual(level, logger.level)
            self.assertEqual(FILENAME, logger.filename)
