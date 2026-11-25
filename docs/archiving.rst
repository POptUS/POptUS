.. _archiver_section:

Archiving
=========
.. note::
    The |poptus| archiving factility can be integrated in methods and models
    transparently for method and model users.  This section is, therefore, only
    useful for method developers that need to use the archiving facility to
    satisfy |poptus| requirements and for model developers that are considering
    the use of the facilities.

|poptus|-based applications couple a |poptus| method code with a computer model
code.  The |poptus| archiving facility is designed based on this generic,
universal application structure so that all applications that use this facility
will write files with similar internal structure.  This common look and feel
benefits not only |poptus| users that might use their model with more than one
method, but also developers.

Design motivations and goals

    * Mimic well-known file formats and interfaces.
    * Capitalize on simple, regular character of data typically stored by
      |poptus| methods and models (|eg| most data tables could be represented by
      "rectangular" spreadsheets).
    * Provide a dedicated abstract interface for writing to and reading from
      archives that is (hopefully) simple due to the regularity of data and that
      could allow for writing to different file formats.
    * Incentivize saving data and metadata on each run of a method to aid in
      rigorous and reproducible |poptus|-based investigations.
    * Provide a simple, stable archiving interface to incentivize model
      developers to store their data and metadata in the same file that stores
      the method results generated from the model.
    * Save results, which we assume are expensive to compute, immediately to
      avoid catastrophic data loss.
    * Limit the possibility of data file corruption.

While the archiver design allows for archiving results to more than one
underlying file format, it is unlikely that |poptus| will support more than one
format at any given time.  Presently results are archived in HDF5-format files.

Archive elements
----------------
Codes can archive data to file as

    * attributes provided as a (key, value) pair,
    * data tables with labeled columns, and
    * evaluation tables.

The data written to general data tables are written at creation and cannot be
altered.

Evaluation tables, which also have labeled columns, are data tables that are
empty at creation, but can have rows of data appended to the table one at a
time.  Users specify at creation both the column names and data types using
NumPy ``dtype`` objects.  As the name implies, each row typically contains
information related to the single evaluation of a function.  However, it could
also be used easily to store information related to iterations of an algorithm.

As a conservative handshake, code must provide to the archiver the current
"evaluation index" that the data to append corresponds to, with the first append
operation passing the index 1.  If the table already holds the data for
evaluations :math:`1, 2, \cdots, n`, then it is an error for the next append
command for the table to have an index different from :math:`n + 1`.  The
one-based indices are stored in the first column of the table and, therefore,
code must must set the first column to ``("index", int)`` in the tables
``dtype`` at creation.

With each append action, an evaluation table is grown by one row.  However, if
codes know or can reasonably estimate the number of rows of data that will be
written, they can specify the number of initial rows at creation, which might
lead to better performance.  The values stored in these initial rows are
initialized to "bad" values -- integers are set to -1, floats are set to NaN,
and strings are empty.  Note that the data table will be grown one row at a time
if calling code appends more rows than they originally set at creation.

For all data tables, developers are encouraged to choose column names that
clearly describe the contents of the column.  For example, if the column stores
values for a physical variable, the column label should indicate the physical
variable and its unit.  This results in data files that are self-documenting and
provides clear communication between the code that created the table and code
that reads the table.

The archiver also provides member functions for reading from an archive
attributes and tables (of either persuasion).

Archive structure
-----------------
|poptus| archive files have an internal, hierarchical structure that are similar
to a directory structure in a file system.  The locations of different elements
in this structure are reference by Posix-format paths, which are represented
programmatically by ``Path`` objects from the ``pathlib`` package.

The hierarchy is built up from groups, with the root group set to ``/``.  Each
group can contain tables or evaluation tables.  Attributes can be assigned to
groups or tables.

For example,

.. code:: bash

    /Group1/Group2/Name
    /Group1/TableA
    /Group1/TableA/Version

specify, respectively, the locations of the

    * "Name" attribute assigned to "Group2",
    * "TableA" data table stored in "Group1", and
    * "Version" attribute assigned to "TableA".

It is an error to create a group or table if its group does not already exist in
the file's structure.  Similarly, it is an error to assign an attribute to a
group or table that does not already exist.

The ``poptus`` package provides ``poptus.ARCHIVE_*`` constants that hold the
locations of fundamental groups in the internal file structure.  All developers
should use these where possible so that archive files have the same structure
and so that their codes adapt automatically to any changes in the structure.

The contents of a |poptus| file are split between the
``potpus.ARCHIVE_MODEL_GROUP`` and ``poptus.ARCHIVE_METHOD_GROUP`` groups.

Model developers are encouraged to archive in the Model group all model
configuration information so that model metadata supports the method results the
model helped generate.  For example, the model's version could be stored in the
attribute

.. code:: python

    potpus.ARCHIVE_MODEL_GROUP.joinpath("ModelVersion")

Model developers that would like to archive model evaluation results are
encouraged to also write these within the Model group.

|poptus| method developers should archive all configuration information directly
in the Method group and all results in its ``poptus.ARCHIVE_RESULTS_GROUP``
subgroup.  The package also provides ``poptus.ARCHIVE_*_ATTR`` constants, such as

    * ``poptus.ARCHIVE_METHOD_NAME_ATTR``,
    * ``poptus.ARCHIVE_METHOD_VERSION_ATTR``, and
    * ``poptus.ARCHIVE_START_TIME_ATTR``,

which specify the locations of several common method attributes.

Archiver creation
-----------------
Archival of data is performed through the creation and use of a |poptus|
archiver object.  Rather than create an archiver object by direct instantiation
of an archiver class, developers should create their dedicated archiver object
with the following function.

.. autofunction:: poptus.create_archiver

Each archiver objects works directly with the single file specified at creation.
Since users typically provide an output filename to methods, a single archiver
object is usually created by the method.  If the method will provide its model
with the possibility of archiving to the same file, the same archiver object can
be provided to the model code.

Archivers write data to files serially.  Therefore, special consideration must
be made in constructing applications that run with MPI.  If a non-parallel
method is run within an MPI environment, which could occur if the model code it
calls is parallelized with MPI, then the application should use only a single,
designated archival MPI process to write to file the method's configurations and
all its results.

If the model code also uses the |poptus| archiving facility and both the model
and method codes will archive to the same file, then the single archival process
should be used by both codes.  Typically, the archival process is the model's
lead process, which aggregates all results generated by the MPI processes into a
single location.

Archiver usage
--------------
.. _`Jupyter book`: https://poptus.github.io/POptUS

Rather than have a file resource open at all times or open/close the file
resource automatically on each file interaction, the archival facility puts file
resource management into the hands of developers |via| the Python context
manager.  To minimize the possibility of file corruption, a code will typically
"open" the single file managed by the archiver briefly each time a group of
related, available results are ready for archival.  For example, a method could
create its file and archive all configuration information at once

.. code:: python

    archiver = poputs.create_archiver(filename, poptus.ARCHIVE_CREATE)

    with archiver.open():
        # Allow for archival of model-specific configuration information
        dataset.archive(archiver)
        model.archive(archiver)

        # Write model information known by and needed by the method
        archiver.write_model_spaces(parameter_order, inner_order)

        # Archive provenance information for user
        archiver.write_platform_information()
        archiver.write_software_environment()

        ...

The archiver's file resource is automatically closed upon exiting the ``with``
block.

Please see the |poptus| `Jupyter book`_ for a detailed example of using the
|poptus| archive facilities in a single application with both the method and
model.

Note that many member functions in the following full interface of the current
|poptus| archiver do **not** open the archiver for writing or reading, but
rather require calling code to open the archive before calling.

.. autoclass:: poptus.Hdf5Archiver
    :members:
    :inherited-members:
