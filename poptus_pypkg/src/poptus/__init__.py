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
    LOG_LEVELS
)

from .AbstractLogger import AbstractLogger
from .StandardLogger import StandardLogger
from .create_logger import create_logger

# ----- Python unittest-based test framework
# Used for automatic test discovery
from .load_tests import load_tests

# Allow users to run full test suite as poptus.test()
from .test import test
