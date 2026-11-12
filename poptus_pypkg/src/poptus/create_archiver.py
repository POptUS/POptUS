from ._constants import (
    ARCHIVE_LOG_TAG, ARCHIVE_VALID_MODES, ARCHIVE_CREATE
)
from .create_logger import create_logger
from .Hdf5Archiver import Hdf5Archiver


def create_archiver(filename, mode, logger=None, force=False):
    """
    Create an archiver object for writing to and accessing data from the
    specified file.  New files are created immediately and populated with
    general |poptus| internal file structure.

    :param filename: Name and path of the file to archive to
    :param mode: File access mode

        * ``ARCHIVE_READONLY`` - open pre-existing file in readonly mode
        * ``ARCHIVE_CREATE`` - create the file from scratch
        * ``ARCHIVE_RESTART`` - open pre-existing file for appending data

    :param logger: ``None`` or logger derived from
        :py:class:`poptus.AbstractLogger`.  If ``None``, then |poptus| default
        logger is used.
    :param force: If ``mode`` is ``ARCHIVE_CREATE`` and a file with the given
        filename already exists, then overwrite the file if True.  This argument
        is ignored otherwise.
    """
    if logger is None:
        logger = create_logger()

    if (not isinstance(mode, str)) or (mode.lower() not in ARCHIVE_VALID_MODES):
        msg = f"Invalid file access mode ({mode})"
        logger.error(ARCHIVE_LOG_TAG, msg)
        raise ValueError(msg)
    overwrite = force if mode.lower() == ARCHIVE_CREATE else False

    return Hdf5Archiver(filename, mode, overwrite, logger)
