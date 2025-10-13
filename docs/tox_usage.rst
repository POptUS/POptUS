Developer Environment
=====================
.. _tox: https://tox.wiki

The |poptus| repository contains a `tox`_ setup that defines different
predefined development tasks, each of which is run in a dedicated Python virtual
environment created and managed automatically by |tox|.

Development with |tox|
----------------------
.. _Oliver Bestwalter: https://www.youtube.com/watch?v=PrAyvH-tm8E

Developers must first install |tox| and make it available as a command line tool
in order to run tasks.  To follow suggestions by `Oliver Bestwalter`_, install
|tox| in a dedicated virtual environment and add it to ``PATH``  by adapting the
following to your setup

.. code-block:: console

    $ /path/to/desired/python -m venv ~/local/venv/.toxbase
    $ ~/local/venv/.toxbase/bin/python -m pip install tox
    $ ln -s ~/local/venv/.toxbase/bin/tox ~/local/bin/tox

    (add ~/local/bin to PATH in shell's configuration file and source)

    $ which tox
    $ tox --version

No default tasks are executed by the calls ``tox`` and ``tox -r``.  The
following tasks can be run from within the ``/path/to/POptUS/poptus_pypkg``
folder hierarchy

* ``tox -e coverage``

  * Execute the full test suite for the package and save coverage results to
    the coverage file.  The task runs the the test on code in the developer's
    clone (``pip install``'s editable mode).
  * The ``COVERAGE_FILE`` environment variable can optionally be set to define
    the name of the file that coverage results will be written to.  By default,
    results are written to ``.coverage_poptus``.

* ``tox -e nocoverage``

  * Execute the full test suite for the package using the code installed into
    Python.

* ``tox -e report``

  * This task should be run after or with ``coverage``
  * Display a code coverage report for the package's full test suite and
    generate XML and HTML versions of the report.
  * The ``COVERAGE_XML`` and ``COVERAGE_HTML`` environment variables can
    optionally be set to define the name of the XML- and HTML-format reports.
    Default report names are ``coverage.xml`` and ``htmlcov``.

* ``tox -e check``

  * Report issues if code does not adhere to project-specific standards.

* ``tox -e html``

  * Generate and render documentation in HTML format

* ``tox -e pdf``

  * Generate and render documentation as a PDF file
  * This task uses ``make`` and requires a LaTeX installation.

Additionally, you can run any combination of the above such as ``tox -e
report,coverage``.

Note that each task can be run as ``tox -r -e <task>`` or ``tox -e <task>``.
Developers are responsible for determining which is correct for their current
situation.

Direct use of |tox| venvs
-------------------------
The virtual environments created automatically by |tox| can be used directly by
developers.  Using the ``coverage`` environment, for example, can be useful
since its editable mode installation can facilitate interactive development and
testing of the Python code.  To run a single test case directly using the
``coverage`` environment, for example, execute

.. code-block:: console

    $ cd /path/to/poptus_pypkg
    $ tox -r -e coverage
    $ . ./.tox/coverage/bin/activate
    $ python -m unittest poptus.tests.TestTemplate
