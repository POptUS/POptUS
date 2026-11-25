Advanced Programmatic Interface
===============================

Logging
-------
.. autoclass:: poptus.AbstractLogger
    :members: level, is_lead_logger, log, warn, error
.. autoclass:: poptus.StandardLogger
    :members: level, log, warn, error
.. autoclass:: poptus.FileLogger
    :members: level, filename, log, warn, error
.. autoclass:: poptus.MpiLeadLogger
    :members: level, is_lead_logger, log, warn, error
.. autoclass:: poptus.MpiWorkerLogger
    :members: level, is_lead_logger, log, warn, error

Archiving
---------
.. autoclass:: poptus.AbstractArchiver
    :members:

Provenance Helper Functions
---------------------------
.. autofunction:: poptus.now_utc
.. autofunction:: poptus.get_username
.. autofunction:: poptus.get_platform_information
.. autofunction:: poptus.get_git_clone_information
.. autofunction:: poptus.get_python_environment
