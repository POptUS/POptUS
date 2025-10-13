Getting Started
===============

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
