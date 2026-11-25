import sys

import datetime as dt


def now_utc():
    """
    :return: Current date/time in UTC as an ISO8601-format string.
    """
    py_version = sys.version_info
    assert py_version.major == 3
    tz_utc = dt.UTC if py_version.minor >= 11 else dt.timezone.utc
    return dt.datetime.now(tz_utc).strftime('%Y-%m-%dT%H:%M:%S.%f UTC')
