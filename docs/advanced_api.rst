Advanced Programmatic Interface
===============================

Logging
-------
.. autoclass:: poptus.AbstractLogger
    :members: level, log, warn, error
.. autoclass:: poptus.StandardLogger
    :members: level, log, warn, error
.. autoclass:: poptus.FileLogger
    :members: level, filename, log, warn, error

Archiving
---------
.. autoclass:: poptus.AbstractArchiver
    :members:
.. autoclass:: poptus.Hdf5Archiver
    :members:
.. autofunction:: poptus.get_username
.. autofunction:: poptus.now_utc
