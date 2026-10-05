import sys

from mpi4py import MPI

import poptus


def main(verbosity):
    # ----- HARDCODED VALUES
    SUCCESS = 0
    FAILURE = 1

    LEAD_MPI_PROCESS = 0
    LEAD_TAG = "MpiLead"
    LOG_MSG = "COMM_WORLD has {} processes"
    DEBUG_MSG = "Logging at debug level {}"
    WARN_MSG = "I don't want to cause a panic.  But, we should look into this."
    ERROR_MSG = "I would like to humbly submit an error message for your review"

    # ----- MPI INITIALIZATION
    MPI_COMM = MPI.COMM_WORLD
    comm_size = MPI_COMM.Get_size()
    rank = MPI_COMM.Get_rank()
    is_lead = (rank == LEAD_MPI_PROCESS)

    # ----- CREATE MPI-AWARE LOGGERS
    logger = poptus.create_logger({"Level": verbosity},
                                  rank=rank, is_lead=is_lead)
    log, debug, warn, error = poptus.create_log_functions(logger, LEAD_TAG)

    # Based on design of these loggers, there is no need for application codes
    # to log based on rank.  In fact, for this test we should **not** log based
    # on rank.
    log(LOG_MSG.format(comm_size))

    for level in range(poptus.LOG_LEVEL_MIN_DEBUG, poptus.LOG_LEVEL_MAX + 1):
        debug(DEBUG_MSG.format(level), level)

    warn(WARN_MSG)

    try:
        error(ValueError, ERROR_MSG)
    except ValueError as err:
        if str(err) != ERROR_MSG:
            sys.exit(FAILURE)

    return SUCCESS


if __name__ == "__main__":
    """
    This is a mock MPI-based application that can be used to test correctness of
    MPI-aware logging.
    """
    assert len(sys.argv[1:]) == 1
    verbosity = int(sys.argv[1])
    sys.exit(main(verbosity))
