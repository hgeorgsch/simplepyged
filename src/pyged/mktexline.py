#! /usr/bin/python

import codecs

from pyged.gedcom import Gedcom
from pyged.report.directline import finddescendant, mkqueue
from pyged.report import Report
from pyged.report.tex import texChapterBuilder as texBuilder

import optparse

parser = optparse.OptionParser()
parser.add_option("-o", "--outfile",
                help="Filename for TeX output", 
		dest="outfile", default="pyged.tex" )
parser.add_option("-i", "--gedcom",
                help="Filename for GEDCOM source", 
		dest="gedcom" )
parser.add_option("-I", "--individual",
                help="Key for the individual whose ancestry to report.",
		dest="indi" )
parser.add_option("-T", "--target",
                help="Key for the individual to search.",
		dest="target" )
parser.add_option("-b", "--bio",
                help="Print individuals with biography.",
		default=False, dest="bio", action="store_true" )
(opt,args) = parser.parse_args()

g = Gedcom( opt.gedcom )
a = finddescendant(g,opt.indi,opt.target)
q = mkqueue(a)
r = Report(g,texBuilder(opt.outfile))
if opt.bio:
    r.listbio(q)
else:
    r.list(q)
