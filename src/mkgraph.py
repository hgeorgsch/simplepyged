#! /usr/bin/python

import codecs

from simplepyged.gedcom import Gedcom
from report.report import Report
from report.graph import Graph
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
parser.add_option("-T", "--target",
                help="Key for the individual to search.",
		dest="target" )
(opt,args) = parser.parse_args()

g = Gedcom( opt.gedcom )
r = Graph(g,texBuilder(opt.outfile))
r.mkgraph(opt.indi,opt.target)
