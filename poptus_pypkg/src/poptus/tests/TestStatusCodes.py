"""
Automatic unit testing of poptus status code definitions
"""

import unittest

from poptus import (
    STATUS_VALID, STATUS_MARGINAL,
    STATUS_INVALID, STATUS_CANCELED, STATUS_FAILED
)


class TestStatusCodes(unittest.TestCase):
    def testOrdering(self):
        # Code should be able to filter results based on following ordering of
        # status codes
        self.assertTrue(STATUS_VALID < STATUS_MARGINAL)
        self.assertTrue(STATUS_MARGINAL < STATUS_INVALID)
        self.assertTrue(STATUS_INVALID < STATUS_CANCELED)
        self.assertTrue(STATUS_CANCELED < STATUS_FAILED)
