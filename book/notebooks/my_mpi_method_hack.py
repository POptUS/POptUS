import subprocess as sbp

from pathlib import Path


def my_mpi_method_hack(logger, mpi_comm, lead_process):
    """
    The standard logging MPI notebook written for users is rendered by
    Jupyter book in a single process created outside of MPI.  However, it's
    example is written with Python code that we want to run so that it generates
    correct, nontrivial MPI-based log output.  In addition, we want that code to
    appear to be code written for distributed parallelization with MPI.

    To accomplish this, the single Jupyter book process calls the Python code,
    which creates a POptUS MPI logger outside of mpi4py.  It then calls this
    function as if each MPI process were calling it.

    To make this hack work, this function needs to run an actual MPI-based
    application with mpi4py and more than one process.  Under the assumption
    that the notebook's call to ``MPI.COMM_WORLD.Get_rank()`` outside of an MPI
    environment returns a rank that is compatible with creating a StandardLogger
    object, the faked MPI logger should return the correct log verbosity level
    and all should function as intended.

    Otherwise, we would like the interface of this function to match that of the
    true implementation - my_mpi_method.py - which is used in the developer
    version of this example.
    """
    N_MPI_PROCESSES = 4
    MPI_EXEC = Path(__file__).parent.joinpath("example_mpi_program.py")

    verbosity = logger.level

    CMD = ["mpirun", "-np", str(N_MPI_PROCESSES),
           "python", "-m", "mpi4py",
           MPI_EXEC, str(verbosity)]
    result = sbp.run(CMD, check=True)
    assert result.returncode == 0
