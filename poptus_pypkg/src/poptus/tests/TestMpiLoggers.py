"""
Automatic unittest of the MpiLeadLogger and MpiWorkerLogger classes as
instantiated appropriately via create_logger with a non-None rank argument.
"""

import io
import copy
import inspect
import unittest

from contextlib import redirect_stderr

import subprocess as sbp

from pathlib import Path

import poptus

_INSTALL_PATH = Path(inspect.getfile(poptus)).resolve().parent
_TEST_PATH = _INSTALL_PATH.joinpath("tests").resolve()
_MPI_EXE = _TEST_PATH.joinpath("test_mpi_logging.py")


class TestMpiLoggers(unittest.TestCase):
    # In addition to testing general functionality of the two classes under
    # test, the test suite must also test all MPI logger creation functionality
    # in create_logger() (i.e., when rank is not None).  Therefore, where
    # possible all loggers used in testing are obtained via create_logger().
    #
    # All tests should suppress writing to stdout/err, but check content of
    # suppressed messages where useful.

    def setUp(self):
        self.__SUCCESS = 0
        self.__N_MPI_PROCESSES = 4

        # From Mpi*Logger classes
        self.__RANK_TAG = "Rank {}"
        self.__LOG_FMT = "[{}] {}"
        self.__WARN_FMT = "[{}] WARNING - {}"
        self.__ERROR_FMT = "[{}] ERROR - {}"
        # Error messages that are generated before a logger object can be
        # created.
        self.__ERR_START = f"[{poptus._constants.POPTUS_LOG_TAG}] ERROR"

        # From test_mpi_logging.py
        self.__LEAD_MPI_PROCESS = 0
        self.__LEAD_TAG = "MpiLead"
        self.__LOG_MSG = "COMM_WORLD has {} processes"
        self.__DEBUG_MSG = "Logging at debug level {}"
        self.__WARN_MSG = (
            "I don't want to cause a panic.  But, we should look into this."
        )
        self.__ERROR_MSG = (
            "I would like to humbly submit an error message for your review"
        )

        self.__ALL_RANKS = set(range(0, self.__N_MPI_PROCESSES))
        self.__WORKER_RANKS = \
            self.__ALL_RANKS.difference({self.__LEAD_MPI_PROCESS})

        # Confirm good configurations
        self.__good_level = poptus.LOG_LEVEL_DEFAULT
        self.__good_cfg = {"Level": self.__good_level}
        self.__good_rank = self.__LEAD_MPI_PROCESS
        poptus.create_logger(self.__good_cfg,
                             rank=self.__good_rank, is_lead=True)
        for rank in self.__ALL_RANKS:
            is_lead = (rank == self.__LEAD_MPI_PROCESS)
            poptus.create_logger(self.__good_cfg, rank=rank, is_lead=is_lead)

    def testBadMpiConfigurations(self):
        # Bad level and rank arguments handled separately below.
        for rank in self.__ALL_RANKS:
            is_lead = (rank == self.__LEAD_MPI_PROCESS)

            # Missing level specification
            bad = {}
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_logger(bad, rank=rank, is_lead=is_lead)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERR_START))

            # Extra configuration values
            bad = copy.deepcopy(self.__good_cfg)
            bad["not a valid key"] = poptus.LOG_LEVEL_DEFAULT
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_logger(bad, rank=rank, is_lead=is_lead)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERR_START))

            # Doesn't work with logging to file
            bad = copy.deepcopy(self.__good_cfg)
            bad[poptus._constants.LOG_FILENAME_KEY] = "log.log"
            bad[poptus._constants.LOG_OVERWRITE_KEY] = False
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(NotImplementedError):
                    poptus.create_logger(bad, rank=rank, is_lead=is_lead)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERR_START))

            # Invalid is_lead arguments
            for bad in [None, 1.1, 0, 1, [True], (True,), {True}]:
                with redirect_stderr(io.StringIO()) as buffer:
                    with self.assertRaises(TypeError):
                        poptus.create_logger(self.__good_cfg,
                                             rank=rank, is_lead=bad)
                # print(buffer.getvalue())
                self.assertTrue(buffer.getvalue().startswith(self.__ERR_START))

    def testBadRanks(self):
        # Note that we aren't testing bad ranks with the lead process since
        # MpiLeadProcess doesn't accept a rank constructor argument and,
        # therefore, never tests the rank argument.

        bad_ranks = [
            "", 1.1, [self.__good_rank], (self.__good_rank,), {self.__good_rank}
        ]
        for bad in bad_ranks:
            for rank in self.__WORKER_RANKS:
                with redirect_stderr(io.StringIO()) as buffer:
                    with self.assertRaises(TypeError):
                        poptus.create_logger(self.__good_cfg,
                                             rank=bad,
                                             is_lead=False)
                # print(buffer.getvalue())
                self.assertTrue(buffer.getvalue().startswith(self.__ERR_START))

        for rank in self.__WORKER_RANKS:
            with redirect_stderr(io.StringIO()) as buffer:
                with self.assertRaises(ValueError):
                    poptus.create_logger(self.__good_cfg,
                                         rank=-1,
                                         is_lead=False)
            # print(buffer.getvalue())
            self.assertTrue(buffer.getvalue().startswith(self.__ERR_START))

    def testBadLevels(self):
        bad_levels = [
            None,
            1.1, float(self.__good_level),
            "", str(self.__good_level),
            [], [self.__good_level],
            set(), {self.__good_level},
            min(poptus.LOG_LEVELS) - 1,
            max(poptus.LOG_LEVELS) + 1
        ]
        for bad in bad_levels:
            bad_cfg = copy.deepcopy(self.__good_cfg)
            bad_cfg["Level"] = bad

            # We can fake an MPI application by choosing different ranks
            for rank in self.__ALL_RANKS:
                is_lead = (rank == self.__LEAD_MPI_PROCESS)
                with redirect_stderr(io.StringIO()) as buffer:
                    with self.assertRaises(ValueError):
                        poptus.create_logger(bad_cfg,
                                             rank=rank, is_lead=is_lead)
                # print(buffer.getvalue())
                self.assertTrue(buffer.getvalue().startswith(self.__ERR_START))

    def testLevel(self):
        for rank in self.__ALL_RANKS:
            is_lead = (rank == self.__LEAD_MPI_PROCESS)
            for level in poptus.LOG_LEVELS:
                cfg = copy.deepcopy(self.__good_cfg)
                cfg["Level"] = level
                logger = poptus.create_logger(cfg,
                                              rank=rank,
                                              is_lead=is_lead)
                self.assertEqual(level, logger.level)

    def testLogErrors(self):
        MSG = "Pointless message that we don't actually want to log"

        for rank in self.__ALL_RANKS:
            is_lead = (rank == self.__LEAD_MPI_PROCESS)
            logger = poptus.create_logger(self.__good_cfg,
                                          rank=rank,
                                          is_lead=is_lead)
            with self.assertRaises(AssertionError):
                logger.log(None, MSG, poptus.LOG_LEVEL_NONE)

    def testLoggingAtAllLevels(self):
        # While we could test MPI-aware logging by simulating an MPI
        # application, I prefer testing through mpi4py to ensure correct
        # end-to-end functionality.  However, we don't need to check this for
        # users who will never use MPI and, therefore, we should not force them
        # to install mpi4py.
        try:
            import mpi4py
        except Exception:
            return

        n_procs = len(self.__ALL_RANKS)
        for verbosity in poptus.LOG_LEVELS:
            code, stdout, stderr = self._call_mpi_exe(
                self.__N_MPI_PROCESSES, verbosity
            )
            self.assertEqual(code, self.__SUCCESS)

            # -- stdout
            # All verbosity levels
            # - All processes should write same warning message to stdout
            # Default logging level and higher
            # - Only lead process logs one line of general information
            # Debugging levels
            # - All processes log one message at each debug level included
            #   by the logger's verbosity level
            n_msgs = n_procs
            if verbosity > poptus.LOG_LEVEL_NONE:
                n_msgs += 1
            if verbosity >= poptus.LOG_LEVEL_MIN_DEBUG:
                n_debug_levels = verbosity - poptus.LOG_LEVEL_MIN_DEBUG + 1
                n_msgs += (n_procs * n_debug_levels)
            self.assertEqual(len(stdout), n_msgs)

            # -- stderr
            # All verbosity levels
            # - All processes should write same error message to stderr
            self.assertEqual(len(stderr), len(self.__ALL_RANKS))

            n_stdout = 0
            n_stderr = 0
            for rank in self.__ALL_RANKS:
                is_lead = (rank == self.__LEAD_MPI_PROCESS)
                if is_lead:
                    tag = self.__LEAD_TAG
                else:
                    tag = self.__RANK_TAG.format(rank)

                # -- stdout
                if is_lead and (verbosity >= poptus.LOG_LEVEL_DEFAULT):
                    expected = self.__LOG_FMT.format(
                        tag, self.__LOG_MSG.format(self.__N_MPI_PROCESSES)
                    )
                    self.assertTrue(expected in stdout)
                    n_stdout += 1
                for level in range(poptus.LOG_LEVEL_MIN_DEBUG, verbosity + 1):
                    expected = self.__LOG_FMT.format(
                        tag, self.__DEBUG_MSG.format(level)
                    )
                    self.assertTrue(expected in stdout)
                    n_stdout += 1
                expected = self.__WARN_FMT.format(tag, self.__WARN_MSG)
                self.assertTrue(expected in stdout)
                n_stdout += 1

                # -- stderr
                expected = self.__ERROR_FMT.format(tag, self.__ERROR_MSG)
                self.assertTrue(expected in stderr)
                n_stderr += 1

            # Sanity check the above loop test structure
            self.assertEqual(n_stdout, n_msgs)
            self.assertEqual(n_stderr, n_procs)

    def _call_mpi_exe(self, n_mpi_processes, verbosity):
        CMD = ["mpirun", "-np", str(n_mpi_processes),
               "coverage", "run",
               "--parallel-mode",
               "--data-file=.coverage_poptus",
               "-m", "mpi4py", str(_MPI_EXE)]

        # try:
        result = sbp.run(CMD + [str(verbosity)],
                         stdin=sbp.DEVNULL,
                         capture_output=True, check=True)
        # except sbp.CalledProcessError as err:
        #     stdout = err.stdout.decode()
        #     stderr = err.stderr.decode()

        #     # Log useful information before reraising
        #     msg = "Unable to run MPI test executable - Return code {}\n"
        #     msg = msg.format(err.returncode)
        #     msg += "\t" + " ".join(err.cmd) + "\n"
        #     if stdout != "":
        #         msg += "\n\tstdout logs\n"
        #         msg += "\t" + "-"*60 + "\n"
        #         for line in stdout.split("\n"):
        #             msg += f"\t{line}\n"
        #     if stderr != "":
        #         msg += "\n\tstderr logs\n"
        #         msg += "\t" + "-"*60 + "\n"
        #         for line in stderr.split("\n"):
        #             msg += f"\t{line}\n"
        #     print(msg)
        #     raise

        stdout = [line for line in result.stdout.decode().split("\n")
                  if line != ""]
        stderr = [line for line in result.stderr.decode().split("\n")
                  if line != ""]
        return result.returncode, stdout, stderr
