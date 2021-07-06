pyged - GEDCOM parser and report generator
==========================================

This project consists of two parts:
`simplepyged` which is a simple GEDCOM parser library,
and `report` which is a report generator depending on 
`simplepyged`.

The report generator is original work, but `simplepyged` 
is a fork of
`dijxtra's project <https://github.com/dijxtra/simplepyged>`_,
which in turn was based on 
`another project <http://ilab.cs.byu.edu/cs460/2006w/assignments/program1.html>`_.

Several changes have been made to the parser, with an object
oriented data model mirroring the GEDCOM model.
It still only recognises a subset of GEDCOM 5.5 tags.

Documentation and Examples
--------------------------

Documentation is in docs/, but it is generally out of date.
Examples of how to use this parser are at docs/examples.
If you want to use `pyged`, please get in touch and I'll see
what I can do in terms of documentation.

License
--------

All code is licensed under GPL v.3 or newer.


Some comments on design
-----------------------

First of all, many attempts have been made to simplify the
code.
In particular, this is evident in the gedcom module.
We have a new common superclass of the
:class:`Gedcom` and :class:`Line` classes, to unify the structure
and provide some related functionality once and for all.
Several attributes from the :class:`Gedcom` class have been 
removed, and are instead generated on the fly by accessor methods.

Some objects which used to be lists are now generators instead,
based on the idea that most of the time, all you want is the
iterator.

The parser methods have been simplified and also changed to comply
more closely with the Gedcom standard.  Whitespace in the value field 
is no longer stripped, and whitespace is now allowed inside xref strings.

In this simplification, we have strived to retain compatibility.
However, in the case of the event classes, this was not possible.
The comma separated place strings are now split into a list of 
strings, to make it easier to use the hierarchical structure
recommended by Gedcom.  To represent dates, we have created a
new :class:`Date` class to handle the many forms of approximate
dates supported in Gedcom.  All use of event objects must be
updated accordingly.
