#!/usr/bin/env python

import sys

from mpi4py import MPI

import poptus

LEAD_PROCESS = 0

# Users specify the log level
verbosity = int(sys.argv[1])

# Standard MPI setup
mpi_comm = MPI.COMM_WORLD
comm_size = mpi_comm.Get_size()
rank = mpi_comm.Get_rank()
is_lead = (rank == LEAD_PROCESS)

# Create MPI-aware log functions
logger = poptus.create_logger({"Level": verbosity}, rank=rank, is_lead=is_lead)
log, log_debug, warn, log_and_abort = \
    poptus.create_log_functions(logger, "MpiTest")

# Log general example information
log(f"Running MPI example with {comm_size} processes")
log(f"The logging process is rank {rank}")
log(f"Logging at verbosity level {verbosity}")

# Simple MPI execution
if rank == LEAD_PROCESS:
    workers = [i for i in range(comm_size) if i != LEAD_PROCESS]
    tasks_all = [1.1 * i for i in range(len(workers))]

    for i, task in zip(workers, tasks_all):
        log_debug(f"Sending task to the rank {i} worker process",
                  poptus.LOG_LEVEL_MIN_DEBUG)
        mpi_comm.send(task, dest=i, tag=1)
else:
    task = mpi_comm.recv(source=LEAD_PROCESS, tag=1)
    log_debug(f"Received task {task} from lead process",
              poptus.LOG_LEVEL_MIN_DEBUG)

    if task == 1.1:
        warn("Are you sure that's the task I should work on?")
