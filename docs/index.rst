|poptus| Python package
=======================
.. _universe: https://github.com/POptUS

|poptus| is a Python package that provides infrastructure and common code that
could be used by other Python packages within the |poptus| `universe`_.

.. note::

    This is being developed as an alpha version.  While all functionality
    offered officially is under test, the code and test suite are still under
    active development.  In addition, the interface of the package will likely
    undergo significant changes as we work toward the first official release.

We have identified two different types of people who might interface with 
the |poptus| package:

1. **Users** of Python code (such as methods, models, & applications) that were
   implemented using the |poptus| package's infrastructure.
2. **Developers** of Python code (such as methods, models, & applications) that would
   like to use the |poptus| package's infrastructure in their codes.

In terms of documentation, the needs and interests of those two groups can be
substantially different.  In such cases the User Guide is structured to present
information for each group in a different subsection whose name clearly
indicates the target user.

.. toctree::
   :numbered:
   :maxdepth: 1
   :caption: User Guide:

   get_started
   logging
   api

.. toctree::
   :numbered:
   :maxdepth: 1
   :caption: Developer Guide:

   contributing
   tox_usage
   advanced_api
