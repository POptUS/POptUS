Getting Started
===============
.. _`mpi4py`: https://mpi4py.readthedocs.io

If users will make use of MPI-aware logging and would like to test this
functionality after installing the |poptus| package, then before installing
|poptus| they should follow `mpi4py`_ documentation to install that package in
conjunction with a compatible MPI implementation.  Note that that ``mpi4py``
does **not** need to be installed to simply use the |poptus| package.

General Installations
---------------------
Eventually this package will be distributed by PyPI for direct installation
|via| |pip|.  However, during this initial alpha development phase, users must
install the package directly from their clone of the |poptus| repository.

Installation from clone
^^^^^^^^^^^^^^^^^^^^^^^
.. _`repository`: https://github.com/POptUS/POptUS

After cloning the |poptus| `repository`_ and activating the desired target
Python environment, execute

.. code-block:: console

    $ cd /path/to/POptUS/poptus_pypkg
    $ python -m pip install .

Testing
-------
The |poptus| package's integrated test suite can be used to test an installation
by executing

.. code-block:: console

    $ python
    >>> import poptus
    >>> poptus.__version__
    <version>
    >>> poptus.test()
        ...
