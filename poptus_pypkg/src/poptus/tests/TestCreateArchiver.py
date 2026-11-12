"""
Automatic unittest of the create_archiver() function.

We test argument errors heavily at this level since users should only be
accessing archivers through this function than through direct instantiation from
concrete archiver classes.
"""

import os
import io
import shutil
import unittest

from pathlib import Path
from contextlib import redirect_stderr

import poptus


class TestCreateArchiver(unittest.TestCase):
    # All tests should suppress writing to stdout/err, but check content of
    # suppressed messages where useful.
    #
    # Since concrete archivers are tested elsewhere, we can assume that all
    # valid archiver objects function as expected.

    def setUp(self):
        self.__ERROR_START = f"[{poptus._constants.ARCHIVE_LOG_TAG}] ERROR"

        self.__dir = Path.cwd().joinpath("delete_me")
        if self.__dir.is_dir():
            shutil.rmtree(self.__dir)
        elif self.__dir.is_file():
            os.remove(self.__dir)
        os.mkdir(self.__dir)

        # Confirm good arguments
        self.__good_fname = self.__dir.joinpath("delete_me.h5")
        self.__good_mode = "w"
        self.__good_logger = poptus.create_logger()
        self.__good_force = False

    def tearDown(self):
        if self.__dir.is_dir():
            shutil.rmtree(self.__dir)

    def testCreation(self):
        self.assertFalse(self.__good_fname.exists())
        archiver = poptus.create_archiver(
            self.__good_fname, self.__good_mode,
            self.__good_logger, self.__good_force
        )
        self.assertTrue(isinstance(archiver, poptus.AbstractArchiver))
        self.assertTrue(self.__good_fname.is_file())
        self.assertEqual(self.__good_fname, archiver.filename)
        self.assertEqual(self.__good_mode, archiver.mode)

        # We can be more demanding since there is only one concrete class
        self.assertTrue(isinstance(archiver, poptus.Hdf5Archiver))

    def testBadFilename(self):
        BAD_PATHS = [
            None, True, False,
            0, 1, 1.1,
            (), [], [self.__good_fname], set(), {self.__good_fname}
        ]

        for bad_fname in BAD_PATHS:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_archiver(
                        bad_fname, self.__good_mode,
                        self.__good_logger, self.__good_force
                    )
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(ValueError):
                poptus.create_archiver(
                    "", self.__good_mode,
                    self.__good_logger, self.__good_force
                )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

    def testBadMode(self):
        BAD_MODES = [
            None, True, False,
            0, 1, 1.1,
            (), [], [self.__good_mode], set(), {self.__good_mode}
        ]
        BAD_MODE_STRS = ["", "rw", "aw", "ar", "rwa", "not a mode"]

        for bad_mode in BAD_MODES:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_archiver(
                        self.__good_fname, bad_mode,
                        self.__good_logger, self.__good_force
                    )
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

        for bad_mode in BAD_MODE_STRS:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_archiver(
                        self.__good_fname, bad_mode,
                        self.__good_logger, self.__good_force
                    )
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

    def testBadForce(self):
        BAD_BOOLS = [
            None,
            1.1,
            (), [], [False], set(), {True}
        ]

        for bad_force in BAD_BOOLS:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_archiver(
                        self.__good_fname, self.__good_mode,
                        self.__good_logger, bad_force
                    )
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

    def testBadLogger(self):
        ERROR_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        BAD_LOGGERS = [
            1, 1.1,
            "", "Logger",
            [], [self.__good_logger],
            set(), {self.__good_logger},
            {}, {"Logger": self.__good_logger}
        ]

        for bad_logger in BAD_LOGGERS:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(TypeError):
                    poptus.create_archiver(
                        self.__good_fname, self.__good_mode,
                        bad_logger, self.__good_force
                    )
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(ERROR_START))
