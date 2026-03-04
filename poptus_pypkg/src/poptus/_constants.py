from pathlib import PurePosixPath


# ----- LOGGING INFRASTRUCTURE
# TODO: Add in sphinx documentation for all these?
# -- public interface
LOG_LEVEL_NONE = 0
LOG_LEVEL_DEFAULT = 1
LOG_LEVEL_MIN_DEBUG = 2
LOG_LEVEL_MAX = 4

LOG_LEVELS = list(range(LOG_LEVEL_NONE, LOG_LEVEL_MAX+1))

# -- private interface
# Logger log tag to use for logging errors detected while constructing loggers
POPTUS_LOG_TAG = "POptUS"

# Keys associated with logger configuration dict
LOG_LEVEL_KEY = "Level"
LOG_FILENAME_KEY = "Filename"
LOG_OVERWRITE_KEY = "Overwrite"

# ----- ARCHIVING INFRASTRUCTURE
ARCHIVE_LOG_TAG = "Archiver"

# We will accept either lowercase or uppercase.  Make these all lowercase so
# that argument error checking can always check with mode.lower()
ARCHIVE_READONLY = "r"
ARCHIVE_CREATE = "w"
ARCHIVE_RESTART = "a"
ARCHIVE_VALID_MODES = [
    ARCHIVE_READONLY, ARCHIVE_CREATE, ARCHIVE_RESTART
]

ARCHIVE_ROOT_GROUP = PurePosixPath("/")
ARCHIVE_MODEL_GROUP = ARCHIVE_ROOT_GROUP.joinpath("Model")
ARCHIVE_DATASET_GROUP = ARCHIVE_MODEL_GROUP.joinpath("Dataset")
ARCHIVE_METHOD_GROUP = ARCHIVE_ROOT_GROUP.joinpath("Method")
ARCHIVE_RESULTS_GROUP = ARCHIVE_METHOD_GROUP.joinpath("Results")

# General attributes
ARCHIVE_METHOD_NAME_ATTR = ARCHIVE_METHOD_GROUP.joinpath("MethodName")
ARCHIVE_METHOD_VERSION_ATTR = ARCHIVE_METHOD_GROUP.joinpath("MethodVersion")
ARCHIVE_USERNAME_ATTR = ARCHIVE_METHOD_GROUP.joinpath("Username")
ARCHIVE_START_TIME_ATTR = ARCHIVE_METHOD_GROUP.joinpath("StartTime")
ARCHIVE_END_TIME_ATTR = ARCHIVE_METHOD_GROUP.joinpath("EndTime")
