Documentation
=============

Tools
-----
.. _`typos`: https://github.com/crate-ci/typos

A GitHub action is run automatically to check for typographic errors in all
documentation and source code in the repository using the `typos`_ tool with our
``typos.toml`` configuration file.  An associated ``typos`` command line tool
can also be installed locally by developers for checking eagerly for mistakes:

.. code:: console

    $ cd /path/to/POptUS
    $ typos --config=typos.toml

Other useful tools are described below with regard to the particular
documentation that they serve.

Guides
------
.. _`Sphinx`: https://www.sphinx-doc.org
.. _`reStructuredText`: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _`autodoc`: https://www.sphinx-doc.org/en/master/tutorial/automatic-doc-generation.html
.. _`Read the Docs`: https://about.readthedocs.com

Both the User and Developer Guides are developed in a single `Sphinx`_ project,
which resides in the ``docs`` folder, for publication |via| `Read the Docs`_.
The guides' contents are assembled from files in ``docs`` and from docstrings of
Python code in the package.  General text is written in `reStructuredText`_.
Python docstrings should be written using the default `autodoc`_ formatting.

Manually maintaining the list of what exceptions are raised by a function or
class is difficult at best since, for example, readers might reasonably assume
that all possible exceptions that could be raised by a function will be noted in
the function's documentation.  This would include all exceptions raised by all
functions called by that function.  Therefore, we do **not** document
exceptions.

Presently, this package does not require the use of type hints.  Similarly,
there is no requirement to specify argument or return types in the docstring.
Note that docstrings do not need to specify the default values of optional
arguments since Sphinx should be able to identify this information in the code
and include it appropriately in the rendered documentation.

The guides can be rendered locally in HTML format using |tox|

.. code:: console

    $ cd /path/to/POptUS/poptus_pypkg
    $ tox -e html
 
with the rendered output available at ``docs/build_html/index.html``.  Similar
commands will generate PDF-format output with the ``pdf`` task.  The
configuration for those two tasks in ``tox.ini`` can be used as a guide for
working with this documentation outside of |tox|.

Examples
--------
.. _`MyST Markdown`: https://jupyterbook.org/en/stable/content/myst.html
.. _`hide and remove`: https://jupyterbook.org/en/stable/interactive/hiding.html
.. _`nbdime`: https://nbdime.readthedocs.io

Examples are provided as a single Jupyter book document that is published on the
repository's GitHub page and that resides in the ``book`` folder.  The book's
contents are assembled from files in the ``book`` folder and from Jupyter
notebooks in ``book/notebooks``.  General text is written in the `MyST
Markdown`_ format.

Notebooks are typically written with a focus on the presentation of content in
rendered output rather than how it is presented when viewed as a Jupyter
notebook in a browser.  In particular, developers adjust cell metadata to `hide
and remove`_ contents to improve the conciseness of the content as well as
readability.  Such cell configuration can also be used to hide or remove cells
with commented out content (|eg| alternate configurations or techniques) that
could be useful for readers who want to interact with the notebook directly to
explore the example beyond the rendered content.

The book can be rendered locally using |tox|

.. code:: console

    $ cd /path/to/POptUS/poptus_pypkg
    $ tox -e book

with the rendered book available at ``book/_build/html/index.html``.

The Python virtual environment (venv) created by the ``book`` task not only
contains all extra external dependencies needed by the notebooks, but also extra
packages that can be useful for developing and reviewing notebook content.  For
example, a developer can create the venv cleanly, activate the venv, and use the
venv for development by executing

.. code:: console

    $ cd /path/to/POptUS/poptus_pypkg
    $ tox -r -e book (this creates/recreates the Jupyter book venv cleanly)
    $ . ./.tox/book/bin/activate
    $ cd ../book/notebooks
    $ jupyter notebook

After altering notebook content, the ``book`` task can be rerun or users can
manually call Jupyter book tools using the content of the ``book`` task's
specification in ``tox.ini`` as a guide.

Note that the venv also includes `nbdime`_ so that users can view diffs using

.. code:: console

    $ nbdiff-web <notebook name>.ipynb

Macro Definitions
-----------------
To aid in presenting uniform content not only within each set of documents but
also across all documents, a set of common macros have been defined for both
documentation tools

* ``docs/sphinx_macros.json``
* ``book/_config.yml``

Please familiarize yourself with this list of macros before altering
documentation and please use the macros throughout your changes and additions.
