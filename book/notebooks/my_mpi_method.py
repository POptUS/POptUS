import poptus


def my_mpi_method(logger, mpi_comm, lead_process):
    log, log_debug, warn, log_and_abort = \
        poptus.create_log_functions(logger, "MpiTest")
    
    # Standard MPI information
    comm_size = mpi_comm.Get_size()
    rank = mpi_comm.Get_rank()
    assert 0 <= lead_process < comm_size

    # Log general example information.  These will only be logged by the lead
    # logger.
    log(f"Running MPI example with {comm_size} processes")
    log(f"The lead logging process is rank {rank}")
    log(f"Logging at verbosity level {logger.level}")

    # Simple MPI execution
    log("Starting computations")
    if rank == lead_process:
        # For this method, it's best if the lead log process is also the lead
        # process so that the logging output is simple and clear.  If this lead
        # process block were to call log() directly, that relationship would be
        # necessary.  Therefore, an improved implementation of this method might
        # be to accept a logger configuration and create the logger object
        # itself to automatically set the lead logger as needed.  The present
        # implementation is maintained so that this code is compatible with the
        # Users' version of this example.
        assert logger.is_lead_logger

        workers = [i for i in range(comm_size) if i != lead_process]
        tasks_all = [1.1 * i for i in range(len(workers))]

        for i, task in zip(workers, tasks_all):
            log_debug(f"Sending {task} task to the rank {i} worker process",
                      poptus.LOG_LEVEL_MIN_DEBUG)
            mpi_comm.send(task, dest=i, tag=1)
    else:
        # There is no point to calling log() in this worker process block.
        task = mpi_comm.recv(source=lead_process, tag=1)
        log_debug(f"Received task {task} from lead process",
                  poptus.LOG_LEVEL_MIN_DEBUG)

        if task == 1.1:
            warn("Are you sure that's the task I should work on?")

    mpi_comm.barrier()
    log("Computations finished successfully")
