"""
Automatic unittest of the create_logger function
"""

import io
import unittest

from pathlib import Path
from contextlib import redirect_stderr

import poptus


class TestCreateLogger(unittest.TestCase):
    # All tests should suppress writing to stdout/err, but check content of
    # suppressed messages where useful.
    #
    # Since concrete loggers are tested elsewhere, we can assume that all valid
    # logger objects function as expected.

    def setUp(self):
        self.__error_start = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"
        self.__valid_levels = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        # Confirm good configurations
        good_level = poptus.LOG_LEVEL_DEFAULT

        self.__good_std_config = {
            poptus._constants.LOG_LEVEL_KEY: good_level
        }
        logger = poptus.create_logger(self.__good_std_config)
        self.assertTrue(isinstance(logger, poptus.StandardLogger))

        good_filename = Path.cwd().joinpath("test.log")
        self.__good_file_config = {
            poptus._constants.LOG_LEVEL_KEY: good_level,
            poptus._constants.LOG_FILENAME_KEY: good_filename,
            poptus._constants.LOG_OVERWRITE_KEY: False
        }
        logger = poptus.create_logger(self.__good_file_config)
        self.assertTrue(isinstance(logger, poptus.FileLogger))

        # Include valid levels in containers
        self.__bad_levels = [
            None,
            1.1, float(good_level),
            "", str(good_level),
            [], [good_level],
            set(), {good_level},
            min(poptus.LOG_LEVELS) - 1,
            max(poptus.LOG_LEVELS) + 1
        ]
        # Include valid configs in containers
        self.__bad_cfg_types = [
            1, 1.1,
            [], [None], [self.__good_std_config],
            set(), {None},
            "bad"
        ]

    def testCreateDefault(self):
        logger = poptus.create_logger()
        self.assertTrue(isinstance(logger, poptus.StandardLogger))
        self.assertEqual(poptus.LOG_LEVEL_DEFAULT, logger.level)

    def testCreateFromNone(self):
        logger = poptus.create_logger(None)
        self.assertTrue(isinstance(logger, poptus.StandardLogger))
        self.assertEqual(poptus.LOG_LEVEL_DEFAULT, logger.level)

    def testBadConfigurationType(self):
        for bad in self.__bad_cfg_types:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_logger(bad)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testBadStdConfigurations(self):
        # Invalid level types
        for level in self.__bad_levels:
            bad = self.__good_std_config.copy()
            bad[poptus._constants.LOG_LEVEL_KEY] = level
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_logger(bad)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Missing level specification
        bad = {}
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Extra configuration values
        bad = self.__good_std_config.copy()
        bad["not a valid key"] = poptus.LOG_LEVEL_DEFAULT
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        bad = self.__good_file_config.copy()
        del bad[poptus._constants.LOG_FILENAME_KEY]
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testBadFileConfigurations(self):
        # Invalid level types for standard logger
        for level in self.__bad_levels:
            bad = self.__good_file_config.copy()
            bad[poptus._constants.LOG_LEVEL_KEY] = level
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_logger(bad)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Missing level specification
        bad = self.__good_file_config.copy()
        del bad[poptus._constants.LOG_LEVEL_KEY]
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Missing overwrite for file logger
        bad = self.__good_file_config.copy()
        del bad[poptus._constants.LOG_OVERWRITE_KEY]
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Extra configuration values
        bad = self.__good_file_config.copy()
        bad["not a valid key"] = poptus.LOG_LEVEL_DEFAULT
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_logger(bad)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testCreateStandardLogger(self):
        for level in self.__valid_levels:
            good = self.__good_std_config.copy()
            good[poptus._constants.LOG_LEVEL_KEY] = level
            logger = poptus.create_logger(good)
            self.assertTrue(isinstance(logger, poptus.StandardLogger))
            self.assertEqual(level, logger.level)

    def testCreateFileLogger(self):
        for level in self.__valid_levels:
            good = self.__good_file_config.copy()
            good[poptus._constants.LOG_LEVEL_KEY] = level
            logger = poptus.create_logger(good)
            self.assertTrue(isinstance(logger, poptus.FileLogger))
            self.assertEqual(level, logger.level)
            self.assertEqual(good[poptus._constants.LOG_FILENAME_KEY],
                             logger.filename)
