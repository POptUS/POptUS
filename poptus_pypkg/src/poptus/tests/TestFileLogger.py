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
    def setUp(self):
        self.__tag = "Unittest"

        self.__dir = Path.cwd().joinpath("delete_me")
        if self.__dir.exists():
            shutil.rmtree(self.__dir)
        os.mkdir(self.__dir)

        self.__fname = self.__dir.joinpath("test.log")

    def tearDown(self):
        if self.__dir.is_dir():
            shutil.rmtree(self.__dir)

    def _load_log(self):
        self.assertTrue(self.__fname.is_file())
        with open(self.__fname, "r") as fptr:
            lines = fptr.readlines()
        return lines

    def testBadLevel(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Confirm good values
        good_filename = self.__fname
        good_level = poptus.LOG_LEVEL_DEFAULT
        good_overwrite = False
        poptus.FileLogger(good_level, good_filename, good_overwrite)

        bad_levels = [
            None, [poptus.LOG_LEVEL_DEFAULT], 1.1,
            float(poptus.LOG_LEVEL_DEFAULT),
            min(poptus.LOG_LEVELS) - 1,
            max(poptus.LOG_LEVELS) + 1
        ]
        for bad in bad_levels:
            if good_filename.exists():
                os.remove(good_filename)

            # Confirm that logger is emitting error message to stderr before
            # raising an exception and keep error messages out of test's
            # outputs.
            self.assertFalse(good_filename.exists())
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.FileLogger(bad, good_filename, good_overwrite)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))
            # Error message not written to file because a bad level prevents the
            # creation of the file logger.
            self.assertFalse(good_filename.exists())

    def testBadFilename(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Confirm good values
        good_filename = self.__fname
        good_level = poptus.LOG_LEVEL_DEFAULT
        good_overwrite = False
        poptus.FileLogger(good_level, good_filename, good_overwrite)

        # Logging is to stderr only in absence of a good filename
        #
        # Confirm that logger is emitting error message to stderr before
        # raising an exception and keep error messages out of test's
        # outputs.
        bad_filenames = [
            None, True, False,
            1, 1.1,
            [], [good_filename], [1.1],
            set(), {good_filename}, {1.1},
            {}, {"a": good_filename}
        ]
        for bad in bad_filenames:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.FileLogger(good_level, bad, good_overwrite)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))

        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.FileLogger(good_level, "", good_overwrite)
        self.assertTrue(buffer.getvalue().startswith(MSG_START))

    def testBadOverwrite(self):
        MSG_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Confirm good values
        good_filename = self.__fname
        good_level = poptus.LOG_LEVEL_DEFAULT
        good_overwrite = False
        poptus.FileLogger(good_level, good_filename, good_overwrite)

        # Logging is to stderr only in absence of a good filename
        #
        # Confirm that logger is emitting error message to stderr before
        # raising an exception and keep error messages out of test's
        # outputs.
        bad_overwrites = [
            None,
            "", "not a boolean",
            1, 1.1,
            [], [good_filename], [1.1],
            set(), {good_filename}, {1.1},
            {}, {"a": good_filename}
        ]
        for bad in bad_overwrites:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.FileLogger(good_level, good_filename, bad)
            self.assertTrue(buffer.getvalue().startswith(MSG_START))

    def testOverwrite(self):
        WARN_START = f"[{poptus._constants.POPTUS_LOG_TAG}] WARNING"
        ERROR_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # Create the log file & check that we can't overwrite
        self.assertFalse(self.__fname.exists())
        with redirect_stdout(io.StringIO()) as buffer:
            logger = poptus.FileLogger(poptus.LOG_LEVEL_DEFAULT,
                                       self.__fname, False)
        self.assertEqual("", buffer.getvalue())
        msg = "That was strange..."
        logger.warn(self.__tag, msg)
        self.assertTrue(self.__fname.exists())
        lines = self._load_log()
        self.assertEqual(1, len(lines))
        self.assertEqual(f"[{self.__tag}] WARNING - {msg}\n", lines[0])

        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(RuntimeError):
                logger = poptus.FileLogger(poptus.LOG_LEVEL_DEFAULT,
                                           self.__fname, False)
        self.assertTrue(buffer.getvalue().startswith(ERROR_START))

        # Warning on overwrite
        self.assertTrue(self.__fname.exists())
        with redirect_stdout(io.StringIO()) as buffer:
            logger = poptus.FileLogger(poptus.LOG_LEVEL_DEFAULT,
                                       self.__fname, True)
        self.assertTrue(buffer.getvalue().startswith(WARN_START))
        # Ensure that the file was really overwritten
        msg += " again?!"
        logger.warn(self.__tag, msg)
        self.assertTrue(self.__fname.exists())
        lines = self._load_log()
        self.assertEqual(1, len(lines))
        self.assertEqual(f"[{self.__tag}] WARNING - {msg}\n", lines[0])

        # Cannot overwrite folders
        self.assertTrue(self.__dir.is_dir())
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(RuntimeError):
                logger = poptus.FileLogger(poptus.LOG_LEVEL_DEFAULT,
                                           self.__dir, True)
        self.assertTrue(buffer.getvalue().startswith(ERROR_START))

    def testLevel(self):
        for level in poptus.LOG_LEVELS:
            logger = poptus.FileLogger(level, self.__fname, False)
            self.assertEqual(level, logger.level)

    def testFilename(self):
        logger = poptus.FileLogger(poptus.LOG_LEVEL_DEFAULT,
                                   self.__fname, False)
        self.assertEqual(self.__fname, logger.filename)

    def testLogErrors(self):
        MSG = "Pointless message that we don't actually want to log"

        # No point in logging with no logging level
        logger = poptus.FileLogger(poptus.LOG_LEVEL_DEFAULT,
                                   self.__fname,
                                   False)
        with self.assertRaises(ValueError):
            logger.log(self.__tag, MSG, poptus.LOG_LEVEL_NONE)

    def testLog(self):
        MSG = "I have something rather important to say"
        EXPECTED = f"[{self.__tag}] {MSG}\n"
        VALID_LEVELS = set(poptus.LOG_LEVELS).difference(
            {poptus.LOG_LEVEL_NONE}
        )

        # Confirm that log file isn't even created
        logger = poptus.FileLogger(poptus.LOG_LEVEL_NONE,
                                   self.__fname,
                                   False)
        for level in VALID_LEVELS:
            self.assertFalse(self.__fname.exists())
            logger.log(self.__tag, MSG, level)
            self.assertFalse(self.__fname.exists())

        # Confirm only written to file when appropriate
        for level in VALID_LEVELS:
            to_stdout = [e for e in VALID_LEVELS if e <= level]
            for msg_level in to_stdout:
                self.assertFalse(self.__fname.exists())
                logger = poptus.FileLogger(level, self.__fname, False)
                logger.log(self.__tag, MSG, msg_level)
                self.assertTrue(self.__fname.exists())
                lines = self._load_log()
                self.assertEqual(1, len(lines))
                self.assertEqual(EXPECTED, lines[0])

                os.remove(self.__fname)

            skipped = [e for e in VALID_LEVELS if e > level]
            for msg_level in skipped:
                self.assertFalse(self.__fname.exists())
                logger.log(self.__tag, MSG, msg_level)
                self.assertFalse(self.__fname.exists())

    def testWarn(self):
        MSG = "I am a warning message.  Take heed!"
        EXPECTED = f"[{self.__tag}] WARNING - {MSG}\n"

        for level in poptus.LOG_LEVELS:
            if self.__fname.exists():
                os.remove(self.__fname)

            logger = poptus.FileLogger(level, self.__fname, False)

            self.assertFalse(self.__fname.exists())
            logger.warn(self.__tag, MSG)
            self.assertTrue(self.__fname.exists())

            lines = self._load_log()
            self.assertEqual(1, len(lines))
            self.assertEqual(EXPECTED, lines[0])

    def testError(self):
        MSG = "Something unthinkably horrible has occurred."
        EXPECTED = f"[{self.__tag}] ERROR - {MSG}\n"

        # These should emit error regardless of level to stderr
        for level in poptus.LOG_LEVELS:
            if self.__fname.exists():
                os.remove(self.__fname)

            logger = poptus.FileLogger(level, self.__fname, False)

            self.assertFalse(self.__fname.exists())
            with redirect_stderr(io.StringIO()) as buffer:
                logger.error(self.__tag, MSG)
            self.assertEqual(EXPECTED, buffer.getvalue())
            self.assertTrue(self.__fname.exists())

            lines = self._load_log()
            self.assertEqual(1, len(lines))
            self.assertEqual(EXPECTED, lines[0])

    def testMixture(self):
        MSG_START = f"[{self.__tag}] ERROR"
        DEBUG_LEVELS = range(poptus.LOG_LEVEL_MIN_DEBUG, poptus.LOG_LEVEL_MAX+1)

        # Sanity check that file isn't being recreated with each log action
        logger = poptus.FileLogger(poptus.LOG_LEVEL_MAX, self.__fname, False)

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
            f"[{self.__tag}] ERROR - Error\n"
        ]

        self.assertFalse(self.__fname.exists())
        logger.log(self.__tag, "Info 1", poptus.LOG_LEVEL_DEFAULT)
        logger.log(self.__tag, "Info 2", poptus.LOG_LEVEL_DEFAULT)
        logger.warn(self.__tag, "Warning 1")
        for level in DEBUG_LEVELS:
            logger.log(self.__tag, f"Debug level {level}", level)
        logger.log(self.__tag, "Info 3", poptus.LOG_LEVEL_DEFAULT)
        logger.warn(self.__tag, "Warning 2")
        with redirect_stderr(io.StringIO()) as buffer:
            logger.error(self.__tag, "Error")
        self.assertTrue(buffer.getvalue().startswith(MSG_START))
        self.assertTrue(self.__fname.exists())

        self.assertEqual(expected, self._load_log())
