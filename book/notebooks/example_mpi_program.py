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

    print(f"MPI Vendor: {MPI.get_vendor()}")
    mpi_env_vars = ['OMPI_COMM_WORLD_SIZE', 'PMI_SIZE', 'MV2_COMM_WORLD_SIZE', 'MPI_LOCALNRANKS']
    present_vars = {var: os.environ.get(var) for var in mpi_env_vars if var in os.environ}
    print(f"Detected Launch Variables: {present_vars}")

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
