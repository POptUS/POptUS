"""
Automatic unittest of the Hdf5Archiver class.
"""

import os
import io
import shutil
import unittest

import numpy as np

from pathlib import Path
from contextlib import (
    redirect_stderr, redirect_stdout
)

import poptus


class TestHf5Archiver(unittest.TestCase):
    def setUp(self):
        self.__REQUIRED_GROUPS = [
            poptus.ARCHIVE_ROOT_GROUP,
            poptus.ARCHIVE_MODEL_GROUP,
            poptus.ARCHIVE_METHOD_GROUP,
            poptus.ARCHIVE_RESULTS_GROUP
        ]

        self.__ERROR_START = f"[{poptus._constants.ARCHIVE_LOG_TAG}] ERROR"
        self.__WARN_START = f"[{poptus._constants.ARCHIVE_LOG_TAG}] WARNING"

        self.__dir = Path.cwd().joinpath("delete_me")
        if self.__dir.is_dir():
            shutil.rmtree(self.__dir)
        elif self.__dir.is_file():
            os.remove(self.__dir)
        os.mkdir(self.__dir)

        # Good arguments that tests can use
        self.__preexisting = self.__dir.joinpath("preexisting_result.h5")
        self.__new_fname = self.__dir.joinpath("new_result.h5")
        self.__logger = poptus.create_logger()
        self.__good_data = np.arange(10).reshape([5, 2])
        self.__good_dtype = np.dtype([("a_1", float), ("a_2", float)])
        self.__good_n_rows = 10
        self.__good_param_order = ["alpha", "beta", "gamma"]
        self.__good_inner_order = np.arange(8)

        # Create a pre-existing file with content
        # - Designed as a checkpoint given for a restart
        archiver = poptus.Hdf5Archiver(
            self.__preexisting, poptus.ARCHIVE_CREATE, False,
            self.__logger
        )
        with archiver.open():
            archiver.write_model_spaces(self.__good_param_order,
                                        self.__good_inner_order)
            archiver.write_software_environment()

        # Create archivers for different file opening modalities
        #
        # The from-scratch object will be used for testing general
        # functionality.
        self.__readonly = poptus.Hdf5Archiver(
            self.__preexisting, poptus.ARCHIVE_READONLY, False,
            self.__logger
        )
        self.__append = poptus.Hdf5Archiver(
            self.__preexisting, poptus.ARCHIVE_RESTART, False,
            self.__logger
        )
        self.__scratch = poptus.Hdf5Archiver(
            self.__new_fname, poptus.ARCHIVE_CREATE, False,
            self.__logger
        )

    def tearDown(self):
        if self.__dir.is_dir():
            shutil.rmtree(self.__dir)

    def testReadOnlyError(self):
        # Type/value checking of arguments done during create_archiver testing.

        # You would never want to overwrite a file that you want to open in
        # readonly mode
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(poptus.LogicError):
                poptus.Hdf5Archiver(
                    self.__preexisting, poptus.ARCHIVE_READONLY, True,
                    self.__logger
                )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

    def testWriteErrors(self):
        # Type/value checking of arguments done during create_archiver testing.

        # Confirm that we can't overwrite unless told to
        self.assertTrue(self.__preexisting.is_file())
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(RuntimeError):
                poptus.Hdf5Archiver(
                    self.__preexisting, poptus.ARCHIVE_CREATE, False,
                    self.__logger
                )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

        # Confirm that we can't overwrite a file that doesn't exist
        fname = self.__dir.joinpath("I_am_a_file_that_does_not.exist")
        self.assertFalse(fname.exists())
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(poptus.LogicError):
                poptus.Hdf5Archiver(
                    fname, poptus.ARCHIVE_CREATE, True,
                    self.__logger
                )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

        # Confirm that we won't overwrite a directory
        self.assertTrue(self.__dir.is_dir())
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(RuntimeError):
                poptus.Hdf5Archiver(
                    self.__dir, poptus.ARCHIVE_CREATE, True,
                    self.__logger
                )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

    def testAppendErrors(self):
        # Type/value checking of arguments done during create_archiver testing.

        # If you want to append, then you definitely don't want to overwrite.
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(poptus.LogicError):
                poptus.Hdf5Archiver(
                    self.__preexisting, poptus.ARCHIVE_RESTART, True,
                    self.__logger
                )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

        # You can't append to a file that doesn't exist
        fname = self.__dir.joinpath("I_am_a_file_that_does_not.exist")
        self.assertFalse(fname.exists())
        with redirect_stderr(io.StringIO()) as buffer:
            with self.assertRaises(poptus.LogicError):
                poptus.Hdf5Archiver(
                    fname, poptus.ARCHIVE_RESTART, False,
                    self.__logger
                )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

    def testOverwrite(self):
        EXTRA_ATTR = poptus.ARCHIVE_MODEL_GROUP.joinpath("extra")
        EXTRA_VALUE = 1.1

        # Create file and add extra content
        fname = self.__dir.joinpath("I_am_a_file_that_does_not.exist")
        archiver = poptus.Hdf5Archiver(
            fname, poptus.ARCHIVE_CREATE, False,
            self.__logger
        )
        with archiver.open():
            archiver.write_attribute(EXTRA_ATTR, EXTRA_VALUE)
            self.assertEqual(EXTRA_VALUE, archiver.read_attribute(EXTRA_ATTR))

        with redirect_stdout(io.StringIO()) as buffer:
            poptus.Hdf5Archiver(
                fname, poptus.ARCHIVE_CREATE, True,
                self.__logger
            )
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__WARN_START))

        # Confirm extra content not present
        self.assertTrue(fname.is_file())
        with archiver.open():
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(poptus.LogicError):
                    archiver.read_attribute(EXTRA_ATTR)
        # print(buffer.getvalue())
        self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

    def testContains(self):
        ITEMS_ALL = self.__REQUIRED_GROUPS

        with self.__append.open():
            for item in ITEMS_ALL:
                self.assertTrue(item in self.__append)

    def testFilename(self):
        self.assertEqual(self.__preexisting, self.__readonly.filename)
        self.assertEqual(self.__new_fname, self.__scratch.filename)
        self.assertEqual(self.__preexisting, self.__append.filename)

    def testMode(self):
        self.assertEqual(poptus.ARCHIVE_READONLY, self.__readonly.mode)
        self.assertEqual(poptus.ARCHIVE_CREATE, self.__scratch.mode)
        self.assertEqual(poptus.ARCHIVE_RESTART, self.__append.mode)

    def testReadParameterOrder(self):
        with self.__append.open():
            parameter_order = self.__append.read_parameter_order()
        self.assertTrue(self.__good_param_order == parameter_order)

    def testReadInnerOrder(self):
        with self.__append.open():
            inner_order = self.__append.read_inner_order()
        self.assertTrue(all(self.__good_inner_order == inner_order))

    def testReadonly(self):
        NEW_TABLE = poptus.ARCHIVE_MODEL_GROUP.joinpath("EarthShattering")
        NEW_GROUP = poptus.ARCHIVE_MODEL_GROUP.joinpath("SuperStuff")
        EXTRA_ATTR = poptus.ARCHIVE_MODEL_GROUP.joinpath("extra")
        EXTRA_VALUE = 1.1
        ITEMS_ALL = self.__REQUIRED_GROUPS

        # Check that we can access all contents ...
        with self.__readonly.open():
            for item in ITEMS_ALL:
                self.assertTrue(item in self.__readonly)

        # But can't write.
        with self.__readonly.open():
            self.assertTrue(NEW_GROUP not in self.__readonly)
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(RuntimeError):
                    self.__readonly.create_group(NEW_GROUP)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

            self.assertTrue(EXTRA_ATTR not in self.__readonly)
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(RuntimeError):
                    self.__readonly.write_attribute(EXTRA_ATTR, EXTRA_VALUE)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

            self.assertTrue(NEW_TABLE not in self.__readonly)
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(RuntimeError):
                    self.__readonly.write_table(NEW_TABLE, self.__good_data)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

            self.assertTrue(NEW_TABLE not in self.__readonly)
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(RuntimeError):
                    self.__readonly.create_evaluation_table(
                        NEW_TABLE, self.__good_dtype, self.__good_n_rows
                    )
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

            # TODO: Try to append to preexisting evaluation table once one is in
            # the file

            # Since this file already contains the model spaces, we can't write
            # them for two reasons.
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(poptus.LogicError):
                    self.__readonly.write_model_spaces(self.__good_param_order,
                                                       self.__good_inner_order)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))

            # Since this file already contains platform info, we can't write
            # them for two reasons.
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(RuntimeError):
                    self.__readonly.write_platform_information()
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERROR_START))
