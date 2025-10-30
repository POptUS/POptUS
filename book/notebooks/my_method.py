import poptus

import numpy as np


def run_method(configuration, model, logger):
    # Setup logging
    DEBUG_0 = poptus.LOG_LEVEL_MIN_DEBUG
    DEBUG_2 = poptus.LOG_LEVEL_MIN_DEBUG + 2

    log, log_debug, warn, log_and_abort = \
        poptus.create_log_functions(logger, "Method")

    # Extract config values & log
    x_0 = np.array(configuration["starting_point"])
    factor = configuration["expert"]["factor"]
    max_iters = configuration["max_iters"]
    threshold = configuration["stopping_criteria"]
    
    log("")
    log("Starting point")
    for i, coordinate in enumerate(x_0):
        log(f"\te_{i+1}\t{coordinate}")
    log(f"Iteration budget = {max_iters}")
    log(f"Stopping criteria = {threshold}")
    log_debug("Expert configuration values", DEBUG_0)
    log_debug(f"\tFactor = {factor}", DEBUG_0)
    log("")

    if threshold >= 1.0e-4:
        warn("Stopping criteria is suspiciously large")

    # Start method
    x_i = x_0.copy()
    for i in range(1, max_iters+1):
        log(f"Iteration {i}")
        f_i = model(x_i)
        if f_i <= threshold:
            break

        x_i *= factor
        log_debug(f"Scaling current point by {factor}", DEBUG_2)

    if f_i > threshold:
        log_and_abort(RuntimeError, "Failed to converge within allotted budget")
    
    log(f"Approximated Solution = {f_i}")
    return f_i
