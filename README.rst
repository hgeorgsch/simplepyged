simplepyged - A simple Python GEDCOM parser
===========================================

Status of parser
----------------

Recognises a subset of GEDCOM 5.5 tags. If you need support for an
unsupported tag, submit an issue (or implement it and send a patch).

Documentation and Examples
--------------------------

Documentation is in docs/. Examples of how to use this parser are at
docs/examples. If you find documentation and/or examples confusing,
let me know and I'll try to fix it.

Licence
--------

All code is licenced under GPL v.3 or newer.

First commit to this repository was based on source from here:
http://ilab.cs.byu.edu/cs460/2006w/assignments/program1.html

This branch
-----------

Several changes have been made in this branch of development,
compared to the work of the previous authors.

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
