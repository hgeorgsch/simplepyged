#! /usr/bin/python


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
parser.add_option("-c", "--chapter",
                help="Make a chapter, rather than a standalone report",
		default=False, dest="chapter", action="store_true" )
parser.add_option("-s", "--section",
                help="Make a chapter, rather than a standalone report",
		default=False, dest="chapter", action="store_true" )
(opt,args) = parser.parse_args()

from simplepyged.gedcom import Gedcom
from report.report import Report
import report.tex as TeX

g = Gedcom( opt.gedcom )

if opt.chapter:
   bld = TeX.texChapterBuilder(opt.outfile,ht="chapter")
elif opt.section:
   bld = TeX.texChapterBuilder(opt.outfile,ht="section")
else:
   bld = TeX.texBuilder(opt.outfile)

r = Report(g,bld)
if opt.desc:
   r.descendants(opt.indi,int(opt.maxgen))
else:
   r.stamtavle(opt.indi,int(opt.maxgen))
