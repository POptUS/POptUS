import poptus


def log_messages(logger, source_name):
    DEBUG_LEVELS_ALL = range(poptus.LOG_LEVEL_MIN_DEBUG,
                             poptus.LOG_LEVEL_MAX + 1)

    log, log_debug, warn, log_and_abort = \
        poptus.create_log_functions(logger, source_name)

    log("General Message")
    for debug_level in DEBUG_LEVELS_ALL:
        log_debug(f"Debug Message Level {debug_level}", debug_level)
    warn("Something is not quite right")
    try:
        log_and_abort(RuntimeError, "Something is definitely wrong")
    except RuntimeError:
        # Pretent that an exception wasn't raised so that notebook execution
        # continues.  This is acceptable since example notebooks don't know that
        # we're using log_and_abort() instead of just logging an error message.
        pass
