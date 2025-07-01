#! /usr/bin/python

import codecs

from .gedcom import Gedcom
from .report import *
from .report.tex import texBuilder

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
parser.add_option("-N", "--ngen",
                help="Number of generations.",
		dest="ngen" )
parser.add_option("-F", "--figure",
                help="Make a figure, as opposed to a standalone document.",
		default=False,dest="figure",action="store_true" )
(opt,args) = parser.parse_args()

g = Gedcom( opt.gedcom )
r = Graph(g,texBuilder(opt.outfile),figure=opt.figure)
if opt.indi and opt.target:
   r.mkgraph(opt.indi,opt.target)
elif opt.indi and opt.ngen:
   r.mkpedigree(opt.indi,int(opt.ngen))
elif opt.target and opt.ngen:
   r.mkdescendants(opt.target,int(opt.ngen))
