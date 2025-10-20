Getting Started
===============
.. _`semantic versioning scheme`: https://semver.org
.. _`Releases`: https://github.com/POptUS/POptUS/releases
.. _`PyPI`: https://pypi.org/project/poptus/

The |poptus| package is released periodically with version numbers following the
`semantic versioning scheme`_.  `Releases`_ are issued only after the package
passes additional review and verification.  Each release corresponds to a commit
on the ``main`` branch that is tagged using its associated version number.  A
source distribution and a universal wheel both constructed from the release
commit are uploaded to `PyPI`_.

General Installations
---------------------

PyPI installation
^^^^^^^^^^^^^^^^^
Since development is in the initial alpha development phase, there is no release
of the package on PyPI yet.  Users must install the package directly from a
clone of the |poptus| repository.

Installation from clone
^^^^^^^^^^^^^^^^^^^^^^^
.. _`repository`: https://github.com/POptUS/POptUS

All commits on the ``main`` branch are either a tagged, official release of the
package or a mature alteration of the package that

* has been reviewed,
* is passing all quality checks (|ie| GitHub actions), and
* should be included in the next release.

After cloning the |poptus| `repository`_, users should typically checkout their
desired release commit.  Bold users can choose to checkout a non-release commit
on ``main``, such as the latest commit, in the spirit of working on the bleeding
edge of |poptus| development.  Using the desired Python environment, install the
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
