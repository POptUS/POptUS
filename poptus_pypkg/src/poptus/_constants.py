# ----- LOGGING INFRASTRUCTURE
# TODO: Add in sphinx documentation for all these?
# -- public interface
LOG_LEVEL_NONE = 0
LOG_LEVEL_DEFAULT = 1
LOG_LEVEL_MIN_DEBUG = 2
LOG_LEVEL_MAX = 3

LOG_LEVELS = list(range(LOG_LEVEL_NONE, LOG_LEVEL_MAX+1))

# -- private interface
# Logger log tag to use for logging errors detected while constructing loggers
POPTUS_LOG_TAG = "POptUS"

# Keys associated with logger configuration dict
LOG_LEVEL_KEY = "Level"
LOG_FILENAME_KEY = "Filename"
LOG_OVERWRITE_KEY = "Overwrite"
