#!/usr/bin/env python

import sys
import poptus

from mpi4py import MPI
from my_mpi_method import my_mpi_method

SUCCESS = 0
FAILURE = 1


def main(verbosity):
    LEAD_PROCESS = 0
    
    # Standard MPI setup
    mpi_comm = MPI.COMM_WORLD
    comm_size = mpi_comm.Get_size()
    rank = mpi_comm.Get_rank()
    is_lead = (rank == LEAD_PROCESS)
    
    # assert comm_size > 1
    
    # Create MPI-aware log functions
    logger = poptus.create_logger({"Level": verbosity}, rank=rank, is_lead=is_lead)
    
    my_mpi_method(logger, mpi_comm, LEAD_PROCESS)

    return SUCCESS

if __name__ == "__main__":
    if len(sys.argv[1:]) != 1:
        print("ERROR: One and only one command line arguments please")
        sys.exit(FAILURE)
    verbosity = int(sys.argv[1])

    sys.exit(main(verbosity))
