.. SimplePyGed documentation master file, created by
   sphinx-quickstart on Mon Oct  4 21:28:44 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst

Overview
--------

This distribution includes two packages. 
The :mod:`simplepyged` package is a simple API for handling
GEDCOM 5.5(.1) files.
The :mod:`report` package provides methods to create reports
(e.g. ahnentafel reports) directly from a GEDCOM file.

Note that the system works directly on the GEDCOM file,
and needs to store the entire contents in memory.
This does mean that it will not scale very well.
It will take time to load the file when you approach 10,000
individual, and if you reach a million, you could run out
of memory.  However, the total time to generate a long ahnentafel
report from this GEDCOM file is not unreasonable compared to other
software.

We have aimed to keep the two packages independent, so that 
:mod:`simplepyged` could be extended to use a database backend to
speed up report generation, without affecting the
:mod:`report` package.

The `pyged.gedcom` package
==========================

General Structures
------------------

At the heart of parser is the :class:`Node` class and its
descendants.  The Gedcom data structure is a tree of such
nodes.
The parser class, :class:`Gedcom`, is a descendant of 
:class:`Node` to form the root of the tree and
to represent an entire Gedcom file.
A file is opened by instantiating an object::

  gedcomfile = Gedcom( "file.ged" )

This will immediately load the file and build a tree, consisting
of various child classes of :class:`Node`.

The non-root nodes of the tree represent lines of the file
and are implemented as the :class:`Line` class and its
descendants.  Some record types and substructures have their
own subclasses to provide additional features.

Classes
-------

Gedcom nodes and structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::

   gedcom.rst
   line.rst
   record.rst
   date.rst

Record types
^^^^^^^^^^^^
Family and Individual records naturally require a number of methods
to process relationships in an easy way, and may include data mining
methods.  Therefore, seperate subclasses are provided for these two
record types.  The other record types do not obviously require any
special methods, but have been created in case this is required later.
All the record classes inherit the :class:`Line` class.

.. toctree::
   
   individual.rst
   family.rst
   uniplemented_records.rst

Event types
^^^^^^^^^^^

.. toctree::
   
   event.rst

Searching and filtering of records
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::

   matching.rst

The report generator
====================
   
.. toctree::

   report.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

