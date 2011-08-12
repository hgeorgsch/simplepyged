.. SimplePyGed documentation master file, created by
   sphinx-quickstart on Mon Oct  4 21:28:44 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst


The simplepyged package
-----------------------

The parser and Gedcom object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::

   gedcom.rst

Gedcom nodes and structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::

   line.rst
   record.rst
   date.rst

Record types
^^^^^^^^^^^^

Family and Individual records naturally require a number of methods
to process relationships in an easy way, and may include data mining
methods.  Therefor, seperata subclasses are provided for these two
record types.  The other record types do not obviously require any
special methods, but have been created in case this is required later.

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

