Getting Started
===============
.. _`semantic versioning scheme`: https://semver.org
.. _`Releases`: https://github.com/POptUS/POptUS/releases
.. _`PyPI`: https://pypi.org/project/poptus/

The |poptus| package is released periodically with version numbers following the
`semantic versioning scheme`_.  `Releases`_ are issued only after the package
passes additional review and verification.  Each release corresponds to a commit
on the ``main`` branch that is tagged using its associated version number (|eg|
``v1.2.3``).  A source distribution and a universal wheel both constructed from
the release commit are uploaded to `PyPI`_.

General Installations
---------------------

PyPI installation
^^^^^^^^^^^^^^^^^
.. note::

    Since development is in the initial alpha development phase, there is no
    release of the package on PyPI yet.  Users must install the package directly
    from a clone of the |poptus| repository.

Installation from clone
^^^^^^^^^^^^^^^^^^^^^^^
.. _`repository`: https://github.com/POptUS/POptUS


After cloning the |poptus| `repository`_, users should typically checkout their
desired official release commit.  Bold users that would like to work on the
bleeding edge of |poptus| development can checkout a desired commit on ``main``
with the understanding that all commits on the ``main`` branch are a mature
alteration of the package that

* has been reviewed,
* is passing all quality checks (|ie| GitHub actions), and
* should be included in the next release.

However, they do not benefit from the extra review and verification carried out
during the release process.

After choosing a commit and using the desired Python environment, install the
package by executing

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
