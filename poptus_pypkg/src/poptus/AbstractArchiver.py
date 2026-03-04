import os
import abc

from pathlib import (
    Path, PurePosixPath
)

from ._constants import (
    LOG_LEVEL_MIN_DEBUG,
    ARCHIVE_LOG_TAG,
    ARCHIVE_VALID_MODES, ARCHIVE_READONLY, ARCHIVE_CREATE, ARCHIVE_RESTART,
    ARCHIVE_ROOT_GROUP,
    ARCHIVE_METHOD_GROUP, ARCHIVE_RESULTS_GROUP,
    ARCHIVE_MODEL_GROUP, ARCHIVE_DATASET_GROUP
)
from .LogicError import LogicError
from .get_python_environment import get_python_environment
from .get_platform_information import get_platform_information
from .create_log_functions import create_log_functions


class AbstractArchiver(metaclass=abc.ABCMeta):

    @staticmethod
    def sanitize_path(path):
        """
        Sanity check contents and homogenize path's type.  In particular, this
        assumes that |poptus| and application code should only be engaging with
        content in the model or method groups.

        Since this is more for internal use, this method isn't integrated into
        the error handling or logging scheme.  Rather, calling code is
        responsible for checking for an acceptable result, logging
        warnings/errors if appropriate, and raising an exception if acceptable.

        :return: ``None`` if an error was found; otherwise, Path as a
            PurePosixPath object
        """
        ROOT_STR = str(ARCHIVE_ROOT_GROUP)
        DATASET_STR = str(ARCHIVE_DATASET_GROUP)
        MODEL_STR = str(ARCHIVE_MODEL_GROUP)
        METHOD_STR = str(ARCHIVE_METHOD_GROUP)

        if not isinstance(path, (str, PurePosixPath)):
            return None

        try:
            posix_path = PurePosixPath(path)
        except Exception:
            return None
        path_str = str(posix_path)

        if  \
                (not path_str.startswith(ROOT_STR)) and \
                (not path_str.startswith(DATASET_STR)) and \
                (not path_str.startswith(MODEL_STR)) and \
                (not path_str.startswith(METHOD_STR)):
            return None

        return posix_path

    @staticmethod
    def _split_path(item_path):
        """
        Path sanitized prior to splitting.

        Since this is more for internal use, this method isn't integrated into
        the error handling or logging scheme.  Rather, calling code is
        responsible for checking for an acceptable result, logging
        warnings/errors if appropriate, and raising an exception if acceptable.

        :return: (path, item_name) as posix-format strings for the given table
            or attribute.  (``None``, ``None``) indicates a failure.
        """
        posix_path = AbstractArchiver.sanitize_path(item_path)
        if posix_path is None:
            return None, None
        name_str = str(posix_path.name)
        parent_str = str(posix_path.parent)
        if (parent_str == "") or (name_str == ""):
            return None, None
        return parent_str, name_str

    def __init__(self, filename, mode, overwrite, logger):
        """
        Abstract base class that defines the interface that concrete |poptus|
        archivers must implement.  In particular, it is an abstraction layer
        that allows |poptus| tools and client model code to write configuration
        information, metadata, and results to a single file without knowing the
        format of the file or how this work is being accomplished.

        While this interface implies the inclusion of multiple concrete
        archiver classes in |poptus|, it is unlikely that there will ever be
        more than one.

        .. todo::
            * This interface is heavily based on HDF5, but seems to be fairly
              generic.  OK?
            * Is this simple of an interface sufficient for all model and
              method use cases?
            * Does the notion of archiver work with Methods as well, which
              might be developed by people outside |poptus|?  Can the archiver
              function if the model and method are running in different
              processes?  Different file systems?

        :param filename: Name and path of the file to archive to
        :param mode: File access mode

            * ARCHIVE_READONLY - open pre-existing file in readonly mode
            * ARCHIVE_CREATE - create the file from scratch
            * ARCHIVE_RESTART - open pre-existing file for appending data

        :param overwrite: If ``mode`` is ``ARCHIVE_CREATE`` and a file with the
            given filename already exists, then overwrite the file if ``True``.
            This must be ``False`` for ``ARCHIVE_READONLY`` and
            ``ARCHIVE_RESTART``.
        :param logger: ``None`` or logger derived from
            :py:class:`poptus.AbstractLogger`.  If ``None``, then |poptus|
            default logger is used.
        """
        super().__init__()

        # ----- SETUP LOG INFRASTRUCTURE
        self._log, self._log_debug, self._warn, self._log_and_abort = \
            create_log_functions(logger, ARCHIVE_LOG_TAG)

        # ----- ERROR CHECK ARGUMENTS
        if not isinstance(filename, (str, Path)):
            msg = "Filename ({}) is neither a string nor a Path object"
            self._log_and_abort(TypeError, msg.format(filename))
        elif isinstance(filename, str) and (filename == ""):
            self._log_and_abort(ValueError, "Empty filename given")
        self.__filename = Path(filename).resolve()

        if not isinstance(overwrite, bool):
            msg = f"overwrite ({overwrite}) is not a bool"
            self._log_and_abort(TypeError, msg)

        if (not isinstance(mode, str)) or \
                (mode.lower() not in ARCHIVE_VALID_MODES):
            msg = f"Invalid file access mode ({mode})"
            self._log_and_abort(ValueError, msg)
        self.__mode = mode.lower()

        if self.__mode == ARCHIVE_READONLY:
            if not self.__filename.is_file():
                msg = f"{self.__filename} does not exist or is not a file"
                self._log_and_abort(RuntimeError, msg)
            if overwrite:
                msg = "Readonly files should never be overwritten"
                self._log_and_abort(LogicError, msg)
            msg = f"Create readonly archiver for {self.__filename}"
            self._log_debug(msg, LOG_LEVEL_MIN_DEBUG)
            self._check_file()
        elif self.__mode == ARCHIVE_CREATE:
            if self.__filename.exists():
                if overwrite:
                    if not self.__filename.is_file():
                        msg = "Cannot overwrite {} since it is not a file"
                        msg = msg.format(self.__filename)
                        self._log_and_abort(RuntimeError, msg)
                    self._warn("Overwriting file")
                    os.remove(self.__filename)
                else:
                    msg = f"{self.__filename} already exists"
                    self._log_and_abort(RuntimeError, msg)
            elif overwrite and (not self.__filename.exists()):
                msg = "Cannot overwrite a file that does not exists ({})"
                self._log_and_abort(LogicError, msg.format(self.__filename))

            msg = f"Archiving to {self.__filename} from scratch"
            self._log_debug(msg, LOG_LEVEL_MIN_DEBUG)
            self._create_file()
        else:
            assert self.__mode == ARCHIVE_RESTART
            if overwrite:
                msg = "Never overwrite a file that will be appended to"
                self._log_and_abort(LogicError, msg)
            elif not self.__filename.exists():
                msg = f"Cannot append to nonexistent file {self.__filename}"
                self._log_and_abort(LogicError, msg)

            msg = f"Registering {self.__filename} for appending to"
            self._log_debug(msg, LOG_LEVEL_MIN_DEBUG)
            self._check_file()

    @property
    def filename(self):
        """
        :return: File presently registered with archiver
        """
        return self.__filename

    @property
    def mode(self):
        """
        :return: File presently registered with archiver
        """
        return self.__mode

    def _create_file(self):
        """
        Create the file from scratch and populate it with the basic, minimal
        internal structure.

        .. todo::
            * Store attributes such as creation datetime, user, system?
        """
        with self.open():
            self.create_group(ARCHIVE_MODEL_GROUP)
            self.create_group(ARCHIVE_METHOD_GROUP)
            self.create_group(ARCHIVE_RESULTS_GROUP)

    def _check_file(self):
        """
        Confirm that the current file already contains the basic, minimal
        internal structure.
        """
        GROUPS_ALL = [ARCHIVE_ROOT_GROUP,
                      ARCHIVE_MODEL_GROUP,
                      ARCHIVE_METHOD_GROUP, ARCHIVE_RESULTS_GROUP]
        with self.open():
            for group in GROUPS_ALL:
                if group not in self:
                    msg = f"{group} does not exist in {self.filename}"
                    self._log_and_abort(LogicError, msg)

    def __contains__(self, item):
        """
        This should only be called if the file is currently open.

        :return: True if the file contains a group, table, or attribute
            associated with the given item
        """
        return self._has_item(item)

    @abc.abstractmethod
    def _has_item(self, path):
        """
        The only intended use of this is for the base class to use a concrete
        class's implementation in the base class's __contains__ member function.

        :param path: Posix-format path of group or table to check for.
        :return: True if the file contains a group, table, or attribute
            associated with the given item
        """
        ...

    @abc.abstractmethod
    def create_group(self, group_name):
        """
        This should only be called if the file is currently open.

        :param group_name: Posix-format path of group including group's name
        """
        ...

    @abc.abstractmethod
    def write_attribute(self, attribute, value):
        """
        Add an attribute to the group or table at the given posix-format path
        and that stores the given value with the given key.  Calling code will
        not be able to alter the value assigned to the attribute once written.

        This should only be called if the file is currently open.

        :param attribute: Posix-format path to attribute including its name
        :param value: Value to assign to attribute
        """
        ...

    @abc.abstractmethod
    def read_attribute(self, attribute):
        """
        Access the given attribute associated with the given group or table.

        This should only be called if the file is currently open.

        :param attribute: Posix-format path to attribute including its name
        """
        ...

    @abc.abstractmethod
    def write_table(self, table_name, data):
        """
        Create a table at the given path with the given name that stores the
        given data.  Calling code will not be able to alter the contents of the
        table once written.

        This should only be called if the file is currently open.

        :param table_name: Posix-format path of table including table's name
        :param data: a numpy array or numpy record array
        """
        ...

    @abc.abstractmethod
    def read_table(self, table_name):
        """
        Access the data in the given table.

        This should only be called if the file is currently open.

        :param table_name: Posix-format path of table including table's name
        """
        ...

    @abc.abstractmethod
    def create_evaluation_table(self, table_name, dtype, n_rows):
        """
        Create a data table at the given path with the given name that will
        hold results associated with each evaluation of an associated model
        function.  Calling code will be able to write results to the table
        using :py:func:`poptus.AbstractArchiver.append_evaluation`.  There is no
        limit to how many row can be written to these tables.

        This should only be called if the file is currently open.

        Concrete implementations of this method must initialize all

        * integer data to -1,
        * floating point data to ``np.nan``, and
        * boolean data to ``False``.

        No other data types are presently recognized for inclusion in an
        evaluation table.

        :param table_name: Posix-format path of table including table's name
        :param dtype: numpy dtype object that specifies the type of data to be
            recorded for each evaluation
        :param n_rows: number of rows to add to table at creation
        """
        ...

    @abc.abstractmethod
    def append_evaluation(self, table_name, index, data):
        """
        Append the given data into the given row of the given pre-existing
        evaluation table.

        Concrete implementations must ensure that data has already been set into
        all evaluations of lower indices and must not have already been set for
        the given evaluation index.

        This should only be called if the file is currently open.

        :param table_name: Posix-format path of table including table's name
        :param index: 1-based index of evaluation that generated data
        :param data: Data to be written to file given in the order used to
            construct the table.
        """
        ...

    def write_model_spaces(self, parameter_order, inner_order):
        """
        Write the given paraemter and inner function element orders to the
        model's portion of the archive.

        This should only be called if the file is currently open.
        """
        if not self._has_item(ARCHIVE_MODEL_GROUP):
            msg = "File is empty or was not created with a model section"
            self._log_and_abort(LogicError, msg)

        for j, parameter in enumerate(parameter_order):
            attr = ARCHIVE_MODEL_GROUP.joinpath(f"Parameter_{j+1}")
            self.write_attribute(attr, parameter)
        if inner_order is not None:
            for i, element in enumerate(inner_order):
                attr = ARCHIVE_MODEL_GROUP.joinpath(f"Inner_{i+1}")
                self.write_attribute(attr, element)

    def read_parameter_order(self):
        """
        This should only be called if the file is currently open.
        """
        parameters_all = []
        j = 1
        while True:
            attr = ARCHIVE_MODEL_GROUP.joinpath(f"Parameter_{j}")
            if attr not in self:
                break
            parameter = self.read_attribute(attr)
            if isinstance(parameter, bytes):
                parameter = parameter.decode()
            parameters_all.append(parameter)
            j += 1

        if not parameters_all:
            msg = "Unable to find parameter space specification"
            self._log_and_abort(RuntimeError, msg)

        return parameters_all

    def read_inner_order(self):
        """
        This should only be called if the file is currently open.
        """
        elements_all = []
        i = 1
        while True:
            attr = ARCHIVE_MODEL_GROUP.joinpath(f"Inner_{i}")
            if attr not in self:
                break
            element = self.read_attribute(attr)
            if isinstance(element, bytes):
                element = element.decode()
            elements_all.append(element)
            i += 1

        if not elements_all:
            msg = "Unable to find inner functions elements specification"
            self._log_and_abort(RuntimeError, msg)

        return elements_all

    def write_platform_information(self):
        """
        """
        group = ARCHIVE_METHOD_GROUP.joinpath("Platform")
        self.create_group(group)

        for key, value in get_platform_information().items():
            self.write_attribute(group.joinpath(key), value)

    def write_software_environment(self):
        """
        .. todo::
            * Write all OpenMP env vars as attributes.  This should include
              GMP_* and KMP_* as well.
        """
        group = ARCHIVE_METHOD_GROUP.joinpath("SoftwareEnvironment")
        self.create_group(group)

        env_py = get_python_environment()
        self.write_attribute(group.joinpath("PythonVersion"),
                             env_py["Python"]["version"])
        self.write_attribute(group.joinpath("PythonCompiler"),
                             env_py["Python"]["compiler"])
        self.write_attribute(group.joinpath("PythonBuild"),
                             env_py["Python"]["build"])

        for key, value in env_py["EnvironmentVariables"].items():
            self.write_attribute(group.joinpath(key), value)

        self.write_table(group.joinpath("Packages"), env_py["Packages"])
