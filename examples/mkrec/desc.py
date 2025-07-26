#! /usr/bin/python

from simplepyged.gedcom import Gedcom
from simplepyged.mkrecords import *
from report.report import Report
from report.tex import texBuilder

# Input GEDCOM file 
g = Gedcom("alrik.ged")

# Input file 2
# Source, page
# submitter
ind = parse_desc("moll",dict=g,source="@S587@",page="s. 204",subm="@X33@")

# Output file
g._print( "desc.ged" )
g._init()

r = Report(g,texBuilder("desc0.tex"))
r.stamtavle( "@I9052@", 9 )
r = Report(g,texBuilder("desc.tex"))
r.descendants( "moll", 9 )
