"""
Automatic unittest of the AbstractArchiver class.

Since there is only one concrete archiver class, most testing of the base class
will be done through testing of Hdf5Archiver and create_archiver().  The general
rule will be to test functionality in the layer closest to the user.  For
instance, testing of argument types passed to this class will be tested on
create_archiver().
"""

import unittest

from pathlib import Path

import poptus


class TestAbstractArchiver(unittest.TestCase):
    def setUp(self):
        self.__POSIX_PATHS = [
            poptus.ARCHIVE_ROOT_GROUP,
            poptus.ARCHIVE_MODEL_GROUP,
            poptus.ARCHIVE_METHOD_GROUP
        ]

        self.__BAD_PATHS = [
            None, True, False,
            0, 1, 1.1,
            (), [], [self.__POSIX_PATHS[0]],
            set(), {self.__POSIX_PATHS[0]},
            "Bad", "C:\\Bad"
        ]

    def testAbstract(self):
        # Confirm that class is abstract and cannot be instantiated
        with self.assertRaises(TypeError):
            poptus.AbstractArchiver(
                Path.cwd().joinpath("delete_me.txt"), "r", False,
                poptus.create_logger()
            )

    def testSanitizePath(self):
        for good in self.__POSIX_PATHS:
            posix_path = poptus.AbstractArchiver.sanitize_path(good)
            self.assertEqual(posix_path, good)
            posix_path = poptus.AbstractArchiver.sanitize_path(str(good))
            self.assertEqual(posix_path, good)

        for bad in self.__BAD_PATHS:
            posix_path = poptus.AbstractArchiver.sanitize_path(bad)
            self.assertIsNone(posix_path)

    def testSplitPath(self):
        # TODO: Test failures
        GROUP_NAME = "group_name"
        TABLE_NAME = "table_name"

        group = poptus.ARCHIVE_MODEL_GROUP.joinpath(GROUP_NAME)
        table = group.joinpath(TABLE_NAME)

        tmp, name = poptus.AbstractArchiver._split_path(group)
        self.assertEqual(str(poptus.ARCHIVE_MODEL_GROUP), tmp)
        self.assertEqual(str(GROUP_NAME), name)

        tmp, name = poptus.AbstractArchiver._split_path(table)
        self.assertEqual(str(group), tmp)
        self.assertEqual(str(TABLE_NAME), name)
