"""
POptUS --- a Python package that collects infrastructure and common code that
could be used by other Python packages within the POptUS universe.
"""

from importlib.metadata import version

__version__ = version("poptus")

# Constant module data attributes
from ._constants import (
    LOG_LEVEL_NONE, LOG_LEVEL_DEFAULT,
    LOG_LEVEL_MIN_DEBUG, LOG_LEVEL_MAX,
    LOG_LEVELS,
    ARCHIVE_READONLY, ARCHIVE_CREATE, ARCHIVE_RESTART,
    ARCHIVE_ROOT_GROUP,
    ARCHIVE_MODEL_GROUP, ARCHIVE_DATASET_GROUP,
    ARCHIVE_METHOD_GROUP, ARCHIVE_RESULTS_GROUP,
    ARCHIVE_METHOD_NAME_ATTR, ARCHIVE_METHOD_VERSION_ATTR,
    ARCHIVE_USERNAME_ATTR,
    ARCHIVE_START_TIME_ATTR, ARCHIVE_END_TIME_ATTR
)

from .LogicError import LogicError

from .AbstractLogger import AbstractLogger
from .StandardLogger import StandardLogger
from .FileLogger import FileLogger
from .create_logger import create_logger
from .create_log_functions import create_log_functions

from .AbstractArchiver import AbstractArchiver
from .Hdf5Archiver import Hdf5Archiver
from .create_archiver import create_archiver

# ----- Python unittest-based test framework
# Used for automatic test discovery
from .load_tests import load_tests

# Allow users to run full test suite as poptus.test()
from .test import test
