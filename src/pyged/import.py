#! /usr/bin/python

from .gedcom import Gedcom
from .gedcom.mkrecords import *
from .report import Report
from .report.tex import texBuilder

import optparse

parser = optparse.OptionParser()
parser.add_option("-i", "--gedcom",
                help="Filename for GEDCOM source", 
		dest="gedcom" )
parser.add_option("-o", "--outfile",
                help="Filename for GEDCOM output", 
		dest="outfile" )
parser.add_option("-s", "--source",
                help="Citation for all the data.",
		dest="src" )
parser.add_option("-p", "--source-page",
                help="Page reference for citation.",
		dest="page" )
parser.add_option("-x", "--submitter",
                help="Xref for submitter record.",
		dest="xref" )
parser.add_option("-A", "--ancestors",
                help="Import ancestors",
		default=False, dest="anc", action="store_true" )
parser.add_option("-D", "--descendants",
                help="Import descendants",
		default=False, dest="desc", action="store_true" )
(opt,args) = parser.parse_args()

# Input GEDCOM file 
g = Gedcom( opt.gedcom )

if opt.anc:
   f = parse_ahnentafel
elif opt.desc:
   f = parse_desc
else:
   raise Exception, "-D or -A option required."

for fn in args:
   ind = f(fn,dict=g,source=opt.src,page=opt.page,subm=opt.xref)

# Output file
g._print( opt.outfile )
g._init()
