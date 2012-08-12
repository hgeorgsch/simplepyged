#! /usr/bin/python

from simplepyged.gedcom import Gedcom
from report.report import Report
from report.tex import texBuilder

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
parser.add_option("-N", "--max-gen",
                help="Number of generations to include",
		default=5, dest="maxgen" )
parser.add_option("-D", "--descendants",
                help="Make a descendants report",
		default=False, dest="desc", action="store_true" )
(opt,args) = parser.parse_args()

g = Gedcom( opt.gedcom )
r = Report(g,texBuilder(opt.outfile))
if opt.desc:
   r.descendants(opt.indi,int(opt.maxgen))
else:
   r.stamtavle(opt.indi,int(opt.maxgen))
