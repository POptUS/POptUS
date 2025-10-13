"""
POptUS --- a Python package that collects infrastructure and common code that
could be used by other Python packages within the POptUS universe.
"""

from importlib.metadata import version

__version__ = version("poptus")

# ----- Python unittest-based test framework
# Used for automatic test discovery
from .load_tests import load_tests

# Allow users to run full test suite as poptus.test()
from .test import test
