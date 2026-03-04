import h5py
import contextlib

import numpy as np

from numbers import Integral

from ._constants import (
    LOG_LEVEL_MIN_DEBUG,
    ARCHIVE_READONLY, ARCHIVE_CREATE, ARCHIVE_RESTART
)
from .LogicError import LogicError
from .AbstractArchiver import AbstractArchiver


class Hdf5Archiver(AbstractArchiver):
    def __init__(self, filename, mode, overwrite, logger):
        """
        Concrete implementation of :py:class:`AbstractArchiver` that can be
        used to store configuration information and results in a single
        HDF5-format.

        Since users should always obtain archiver objects from
        :py:func:`create_archiver`, this class should never be instantiated
        directly.

        Please see the :py:class:`AbstractArchiver` documentation for more
        information on arguments and what actions are taken upon instantiation.
        """
        # Internal file object.  None indicates that the file is *not* open.
        self.__h5 = None

        super().__init__(filename, mode, overwrite, logger)

    @contextlib.contextmanager
    def open(self):
        """
        Open the archiver's file within a context so that code can write to the
        file.  The intent is that this should usually be called by |poptus|
        methods only.  However, applications that would also like to archive
        their own setup and results should also use this interface.
        """
        assert self.__h5 is None

        if self.mode == ARCHIVE_READONLY:
            mode = "r"
        else:
            assert self.mode in [ARCHIVE_CREATE, ARCHIVE_RESTART]
            mode = "a"

        try:
            self.__h5 = h5py.File(self.filename, mode)
            yield self
        finally:
            self.__h5.close()
            self.__h5 = None
            self._log_debug(f"{self.filename} closed", LOG_LEVEL_MIN_DEBUG)

    def _has_item(self, path):
        if self.__h5 is None:
            msg = f"Open file before checking existence of {path}"
            self._log_and_abort(LogicError, msg)

        # Groups and tables
        if str(AbstractArchiver.sanitize_path(path)) in self.__h5:
            return True
        return str(path.name) in self.__h5[str(path.parent)].attrs

    def create_group(self, group_name):
        if self.__h5 is None:
            msg = f"Open file before creating group {group_name}"
            self._log_and_abort(LogicError, msg)

        path, name = AbstractArchiver._split_path(group_name)
        if path not in self.__h5:
            msg = f"{path} does not exist in {self.filename}"
            self._log_and_abort(LogicError, msg)
        elif name in self.__h5[path]:
            msg = f"Group {name} already exists in {self.filename}"
            self._log_and_abort(LogicError, msg)

        self._log_debug(f"Creating group {group_name}", LOG_LEVEL_MIN_DEBUG)

        try:
            self.__h5[path].create_group(name)
        except Exception as e:
            msg = f"Unable to create group {name} in {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)

    def write_attribute(self, attribute, value):
        path, key = AbstractArchiver._split_path(attribute)

        if self.__h5 is None:
            msg = f"Open file before writing attribute {key}"
            self._log_and_abort(LogicError, msg)
        elif path not in self.__h5:
            msg = f"{path} does not exist in {self.filename}"
            self._log_and_abort(LogicError, msg)
        elif key in self.__h5[path].attrs:
            msg = "Attribute {} already exists at {} in {}"
            self._log_and_abort(LogicError,
                                msg.format(key, path, self.filename))

        if isinstance(value, str):
            dtype = h5py.string_dtype('ascii', len(value))
            value = np.array(value, dtype=dtype)

        msg = f"Writing attribute {key} = {value}"
        self._log_debug(msg, LOG_LEVEL_MIN_DEBUG)

        try:
            self.__h5[path].attrs[key] = value
        except Exception as e:
            msg = f"Unable to write attribute {key} in {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)

    def read_attribute(self, attribute):
        path, key = AbstractArchiver._split_path(attribute)

        if self.__h5 is None:
            msg = f"Open file before reading attribute {attribute}"
            self._log_and_abort(LogicError, msg)
        elif path not in self.__h5:
            msg = f"{path} does not exist in {self.filename}"
            self._log_and_abort(LogicError, msg)
        elif key not in self.__h5[path].attrs:
            msg = "Attribute {} does not exist in {}"
            self._log_and_abort(LogicError,
                                msg.format(attribute, self.filename))

        try:
            value = self.__h5[path].attrs[key]
        except Exception as e:
            msg = f"Unable to read attribute {key} in {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)

        self._log_debug(f"Reading attribute {attribute} = {value}",
                        LOG_LEVEL_MIN_DEBUG + 1)

        return value

    def write_table(self, table_name, data):
        """
        .. todo::
            * Check type and shape of data?
        """
        if self.__h5 is None:
            msg = f"Open file before writing table {table_name}"
            self._log_and_abort(LogicError, msg)

        path, name = AbstractArchiver._split_path(table_name)
        if path not in self.__h5:
            msg = f"{path} does not exist in {self.filename}"
            self._log_and_abort(LogicError, msg)
        elif name in self.__h5[path]:
            msg = f"Table {name} already exists in {self.filename}"
            self._log_and_abort(LogicError, msg)

        self._log_debug(f"Writing table {table_name}", LOG_LEVEL_MIN_DEBUG)

        try:
            self.__h5[path].create_dataset(name, data=data)
        except Exception as e:
            msg = f"Unable to write table {table_name} in {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)

    def read_table(self, table_name):
        name_str = str(AbstractArchiver.sanitize_path(table_name))
        if self.__h5 is None:
            msg = f"Open file before reading table {table_name}"
            self._log_and_abort(LogicError, msg)
        elif name_str not in self.__h5:
            msg = f"{table_name} does not exist in {self.filename}"
            self._log_and_abort(LogicError, msg)

        self._log_debug(f"Reading table {table_name}",
                        LOG_LEVEL_MIN_DEBUG + 1)

        try:
            data = np.array(self.__h5[name_str])
        except Exception as e:
            msg = f"Unable to read table {table_name} from {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)

        return data

    def create_evaluation_table(self, table_name, dtype, n_rows):
        """
        .. todo::
            * Does this work if n_rows=0?
            * Check type of dtype?
            * If a column is a string, what should we do?
        """
        if self.__h5 is None:
            msg = f"Open file before creating table {table_name}"
            self._log_and_abort(LogicError, msg)
        elif not isinstance(n_rows, Integral):
            msg = f"n_rows ({n_rows}) is not an integer"
            self._log_and_abort(TypeError, msg)
        elif n_rows <= 0:
            msg = f"n_rows ({n_rows}) is nonpositive"
            self._log_and_abort(ValueError, msg)

        data = np.zeros(n_rows, dtype=dtype)
        for key in dtype.names:
            if dtype[key] == int:
                data[key] = -1
            elif dtype[key] == float:
                data[key] = np.nan
            elif dtype[key] == bool:
                data[key] = False
            elif dtype[key] == 'O':
                data[key] = None
            elif str(dtype[key]).startswith('|S'):
                data[key] = "None"
            else:
                msg = f"Unknown type {dtype[key]} for column {key}"
                self._log_and_abort(TypeError, msg)

        path, name = AbstractArchiver._split_path(table_name)
        if path not in self.__h5:
            msg = f"{path} does not exist in {self.filename}"
            self._log_and_abort(LogicError, msg)
        elif name in self.__h5[path]:
            msg = f"Table {name} already exists in {self.filename}"
            self._log_and_abort(LogicError, msg)

        self._log_debug(f"Creating table {table_name}", LOG_LEVEL_MIN_DEBUG)

        try:
            self.__h5[path].create_dataset(name, data=data, maxshape=(None,))
        except Exception as e:
            msg = f"Unable to create table {table_name} in {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)

    def append_evaluation(self, table_name, index, data):
        """
        .. todo::
            * Check data argument?
        """
        if self.__h5 is None:
            msg = f"Open file before appending to {table_name}"
            self._log_and_abort(LogicError, msg)

        if not isinstance(index, Integral):
            msg = f"index ({index}) is not an integer"
            self._log_and_abort(TypeError, msg)
        elif index <= 0:
            raise ValueError(f"Nonpositive evaluation index ({index})")

        table_str = str(AbstractArchiver.sanitize_path(table_name))
        if table_str not in self.__h5:
            msg = f"{table_name} does not exist in {self.filename}"
            self._log_and_abort(LogicError, msg)

        try:
            table = self.__h5[table_str]
        except Exception as e:
            msg = f"Unable to access table {table_name} in {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)

        self._log_debug(f"Appending data to {table_name}",
                        LOG_LEVEL_MIN_DEBUG + 1)

        if index > 1 and (table["index"][index - 2] == -1):
            msg = f"Skipped evaluation {index-1} in {table_name}"
            self._log_and_abort(LogicError, msg)
        if index > len(table):
            try:
                table.resize(index, axis=0)
            except Exception as e:
                msg = f"Unable to resize {table_name} in {self.filename}\n"
                msg += str(e)
                self._log_and_abort(RuntimeError, msg)
        elif table["index"][index - 1] != -1:
            msg = f"Evaluation {index} already has data in {table_name}"
            self._log_and_abort(LogicError, msg)

        try:
            table[index - 1] = tuple([index] + list(data))
        except Exception as e:
            msg = f"Unable to append to {table_name} in {self.filename}\n"
            msg += str(e)
            self._log_and_abort(RuntimeError, msg)
