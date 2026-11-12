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

# ----- COMPUTATION STATUS CODES
# As per requirements
#       Valid < Marginal < Invalid < Canceled < Failed
STATUS_VALID = 0
STATUS_MARGINAL = 1
STATUS_INVALID = 2
STATUS_CANCELED = 3
STATUS_FAILED = 4

STATUS_CODE_NAMES = {
    STATUS_VALID: "Valid",
    STATUS_MARGINAL: "Marginal",
    STATUS_INVALID: "Invalid",
    STATUS_CANCELED: "Canceled",
    STATUS_FAILED: "Failed"
}
