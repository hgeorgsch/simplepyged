# pyged - GEDCOM parser and report generator

This project provides the `pyged` package for python.
providing a portfolio of scripts as well as two library
modules.

+ `pyged.gedcom` is a simple GEDCOM parser library
+ `pyged.report` is a library to produce reports, particularly in
  TeX format, from GEDCOM files parsed by the above library.

The report generator is original work, while the GEDCOM parser
was originally a fork of
[dijxtra's project](https://github.com/dijxtra/simplepyged),
which in turn was based on 
[another project](http://ilab.cs.byu.edu/cs460/2006w/assignments/program1.html).
Several changes have been made to the parser, with an object
oriented data model mirroring the GEDCOM model.
It still only recognises a subset of GEDCOM 5.5 tags.

## Documentation and Examples

+ Documentation under `docs/`
+ Examples under `examples/`

Documentation and examples are generally long out of date. (**TODO**)
If you want to use `pyged`, please get in touch and I'll see
what I can do in terms of documentation.

## License

All code is licensed under GPL v.3 or newer.


## Some comments on design

First of all, many attempts have been made to simplify the
code.
In particular, this is evident in the gedcom module.
We have a new common superclass of the
`Gedcom` and `Line` classes, to unify the structure
and provide some related functionality once and for all.
Several attributes from the `Gedcom` class have been 
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
new `Date` class to handle the many forms of approximate
dates supported in Gedcom.  All use of event objects must be
updated accordingly.

## Version History

+ v0.2.0.  First version released on PyPI - still rudimentary and undocumented.
+ v0.1.1.  Preliminary version, debugging the packaging info for PyPI
+ v0.1.  Unreleased versions, available on github.
