#! /usr/bin/python

import codecs

from pyged.gedcom import Gedcom
from pyged.report.directline import finddescendant, mklines
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
(opt,args) = parser.parse_args()

g = Gedcom( opt.gedcom )
a = finddescendant(g,opt.indi,opt.target)
r = mklines(a)
file = codecs.open( opt.outfile, "w", "UTF-8" )
for l in r: file.write(l + "\n")
file.close()
