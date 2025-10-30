import poptus
import functools

import numpy as np


def model_to_wrap(x, p, log_debug):
    # Accept log_debug function rather than logger to avoid recreating log
    # functions with each model evaluation.
    value = np.linalg.norm(x, ord=p)
    log_debug(f"Value = {value} at {x}", poptus.LOG_LEVEL_MIN_DEBUG)
    return value

def construct_model(configuration):
    p = configuration["Numerics"]["p"]
    logger = poptus.create_logger(configuration["Logging"])
    log, log_debug, _, _ = poptus.create_log_functions(logger, "Model")
    log("")
    log(f"Creating model with p={p}")
    log("")

    return functools.partial(model_to_wrap, p=p, log_debug=log_debug)
