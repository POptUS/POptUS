"""
Automatic unittest of the FileLogger class
"""

import os
import io
import shutil
import unittest

from pathlib import Path
from contextlib import (
    redirect_stdout, redirect_stderr
)

import poptus


class TestFileLogger(unittest.TestCase):
    # All tests should suppress writing to stderr, but check content of
    # suppressed messages where useful.

    def setUp(self):
        self.__dir = Path.cwd().joinpath("delete_me")
        if self.__dir.exists():
            shutil.rmtree(self.__dir)
        os.mkdir(self.__dir)

        self.__valid_levels = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        self.__tag = "Unittest"
        self.__warn_start = f"[{poptus._constants.POPTUS_LOG_TAG}] WARNING"
        self.__error_start = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Confirm good configurations
        self.__good_level = poptus.LOG_LEVEL_DEFAULT
        self.__good_filename = self.__dir.joinpath("test.log")
        self.__good_overwrite = False
        poptus.FileLogger(self.__good_filename,
                          self.__good_overwrite,
                          self.__good_level)

        # Include valid arguments in containers
        self.__bad_levels = [
            None,
            1.1, float(self.__good_level),
            "", str(self.__good_level),
            [], [self.__good_level],
            set(), {self.__good_level},
            {}, {"Level": self.__good_level},
            min(poptus.LOG_LEVELS) - 1,
            max(poptus.LOG_LEVELS) + 1
        ]
        self.__bad_filenames = [
            None, True, False,
            1, 1.1,
            [], [self.__good_filename], [str(self.__good_filename)],
            set(), {self.__good_filename}, {str(self.__good_filename)},
            {}, {"Filename": self.__good_filename},
            {"Filename": str(self.__good_filename)}
        ]
        self.__bad_overwrites = [
            None,
            0, 1, 1.1,
            "", "not a boolean",
            [], [self.__good_overwrite],
            set(), {self.__good_overwrite},
            {}, {"a": self.__good_overwrite}
        ]

    def tearDown(self):
        if self.__dir.is_dir():
            shutil.rmtree(self.__dir)

    def _load_log(self):
        self.assertTrue(self.__good_filename.is_file())
        with open(self.__good_filename, "r") as fptr:
            lines = fptr.readlines()
        return lines

    def testBadFilename(self):
        for bad in self.__bad_filenames:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.FileLogger(bad,
                                      self.__good_overwrite,
                                      self.__good_level)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.FileLogger("",
                                  self.__good_overwrite,
                                  self.__good_level)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testBadOverwrite(self):
        for bad in self.__bad_overwrites:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.FileLogger(self.__good_filename,
                                      bad,
                                      self.__good_level)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testBadLevel(self):
        for bad in self.__bad_levels:
            self.assertFalse(self.__good_filename.exists())
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.FileLogger(self.__good_filename,
                                      self.__good_overwrite,
                                      bad)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__error_start))
            # Error message not written to file because a bad level prevents the
            # creation of the file logger.
            self.assertFalse(self.__good_filename.exists())

    def testOverwrite(self):
        MSG_1 = "That was strange..."
        EXPECTED_MSG_1 = f"[{self.__tag}] WARNING - {MSG_1}\n"
        MSG_2 = "What?!  Again?!"
        EXPECTED_MSG_2 = f"[{self.__tag}] WARNING - {MSG_2}\n"

        self.assertFalse(self.__good_filename.exists())
        logger = poptus.FileLogger(self.__good_filename,
                                   False,
                                   self.__good_level)
        # Create the log file & check that we can't overwrite
        logger.warn(self.__tag, MSG_1)
        lines = self._load_log()
        self.assertEqual(1, len(lines))
        self.assertEqual(EXPECTED_MSG_1, lines[0])

        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(RuntimeError):
                logger = poptus.FileLogger(self.__good_filename,
                                           False,
                                           self.__good_level)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

        # Warning on overwrite
        self.assertTrue(self.__good_filename.is_file())
        with redirect_stdout(io.StringIO()) as buffer:
            logger = poptus.FileLogger(self.__good_filename,
                                       True,
                                       self.__good_level)
        self.assertTrue(buffer.getvalue().startswith(self.__warn_start))
        self.assertFalse(self.__good_filename.exists())
        logger.warn(self.__tag, MSG_2)
        self.assertTrue(self.__good_filename.is_file())
        lines = self._load_log()
        self.assertEqual(1, len(lines))
        self.assertEqual(EXPECTED_MSG_2, lines[0])
        self.assertNotEqual(EXPECTED_MSG_1, EXPECTED_MSG_2)

        # Cannot overwrite folders
        self.assertTrue(self.__dir.is_dir())
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(RuntimeError):
                logger = poptus.FileLogger(self.__dir,
                                           True,
                                           self.__good_level)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__error_start))

    def testLevel(self):
        for level in poptus.LOG_LEVELS:
            logger = poptus.FileLogger(self.__good_filename,
                                       self.__good_overwrite,
                                       level)
            self.assertEqual(level, logger.level)

    def testDefaultLevel(self):
        logger = poptus.FileLogger(self.__good_filename,
                                   self.__good_overwrite)
        self.assertEqual(poptus.LOG_LEVEL_DEFAULT, logger.level)

    def testFilename(self):
        logger = poptus.FileLogger(self.__good_filename,
                                   self.__good_overwrite,
                                   self.__good_level)
        self.assertEqual(self.__good_filename, logger.filename)

    def testLogErrors(self):
        MSG = "Pointless message that we don't actually want to log"

        logger = poptus.FileLogger(self.__good_filename,
                                   self.__good_overwrite,
                                   self.__good_level)
        with self.assertRaises(AssertionError):
            logger.log(self.__tag, MSG, poptus.LOG_LEVEL_NONE)

    def testLog(self):
        MSG = "I have something rather important to say"
        EXPECTED_MSG = f"[{self.__tag}] {MSG}\n"

        # Confirm that log file isn't even created
        logger = poptus.FileLogger(self.__good_filename,
                                   False,
                                   poptus.LOG_LEVEL_NONE)
        self.assertFalse(self.__good_filename.exists())
        for level in self.__valid_levels:
            logger.log(self.__tag, MSG, level)
            self.assertFalse(self.__good_filename.exists())

        for level in self.__valid_levels:
            to_stdout = [e for e in self.__valid_levels if e <= level]
            for msg_level in to_stdout:
                self.assertFalse(self.__good_filename.exists())
                logger = poptus.FileLogger(self.__good_filename,
                                           self.__good_overwrite,
                                           level)
                logger.log(self.__tag, MSG, msg_level)
                # print(level, msg_level)
                lines = self._load_log()
                self.assertEqual(1, len(lines))
                self.assertEqual(EXPECTED_MSG, lines[0])

                os.remove(self.__good_filename)

            skipped = [e for e in self.__valid_levels if e > level]
            for msg_level in skipped:
                self.assertFalse(self.__good_filename.exists())
                logger.log(self.__tag, MSG, msg_level)
                self.assertFalse(self.__good_filename.exists())

    def testWarn(self):
        MSG = "I am a warning message.  Take heed!"
        EXPECTED_MSG = f"[{self.__tag}] WARNING - {MSG}\n"

        for level in poptus.LOG_LEVELS:
            if self.__good_filename.exists():
                os.remove(self.__good_filename)

            logger = poptus.FileLogger(self.__good_filename,
                                       self.__good_overwrite,
                                       level)

            self.assertFalse(self.__good_filename.exists())
            logger.warn(self.__tag, MSG)
            lines = self._load_log()
            self.assertEqual(1, len(lines))
            self.assertEqual(EXPECTED_MSG, lines[0])

    def testError(self):
        MSG = "Something unthinkably horrible has occurred."
        EXPECTED_MSG = f"[{self.__tag}] ERROR - {MSG}\n"

        for level in poptus.LOG_LEVELS:
            if self.__good_filename.exists():
                os.remove(self.__good_filename)

            logger = poptus.FileLogger(self.__good_filename,
                                       self.__good_overwrite,
                                       level)

            self.assertFalse(self.__good_filename.exists())
            with redirect_stderr(io.StringIO()) as buffer:
                logger.error(self.__tag, MSG)
            self.assertEqual(EXPECTED_MSG, buffer.getvalue())
            lines = self._load_log()
            self.assertEqual(1, len(lines))
            self.assertEqual(EXPECTED_MSG, lines[0])

    def testMixture(self):
        ERROR_MSG = "Oops!"
        EXPECTED_ERROR_MSG = f"[{self.__tag}] ERROR - {ERROR_MSG}\n"
        DEBUG_LEVELS = range(poptus.LOG_LEVEL_MIN_DEBUG, poptus.LOG_LEVEL_MAX+1)

        # Sanity check that file isn't being recreated with each log action
        logger = poptus.FileLogger(self.__good_filename,
                                   False,
                                   poptus.LOG_LEVEL_MAX)

        expected = [
            f"[{self.__tag}] Info 1\n",
            f"[{self.__tag}] Info 2\n",
            f"[{self.__tag}] WARNING - Warning 1\n",
        ]
        for level in DEBUG_LEVELS:
            expected += [f"[Unittest] Debug level {level}\n"]
        expected += [
            f"[{self.__tag}] Info 3\n",
            f"[{self.__tag}] WARNING - Warning 2\n",
            EXPECTED_ERROR_MSG
        ]

        self.assertFalse(self.__good_filename.exists())
        logger.log(self.__tag, "Info 1", poptus.LOG_LEVEL_DEFAULT)
        logger.log(self.__tag, "Info 2", poptus.LOG_LEVEL_DEFAULT)
        logger.warn(self.__tag, "Warning 1")
        for level in DEBUG_LEVELS:
            logger.log(self.__tag, f"Debug level {level}", level)
        logger.log(self.__tag, "Info 3", poptus.LOG_LEVEL_DEFAULT)
        logger.warn(self.__tag, "Warning 2")
        with redirect_stderr(io.StringIO()) as buffer:
            logger.error(self.__tag, ERROR_MSG)
        self.assertEqual(EXPECTED_ERROR_MSG, buffer.getvalue())
        self.assertEqual(expected, self._load_log())
