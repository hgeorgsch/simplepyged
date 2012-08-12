#! /usr/bin/python

from simplepyged.gedcom import Gedcom
from simplepyged.mkrecords import *
from report.report import Report
from report.tex import texBuilder

g = Gedcom("alrik.ged")
ind = parse_desc("moll",dict=g,source="@S587@",page="s. 204",subm="@X33@")

g._print( "desc.ged" )
g._init()
r = Report(g,texBuilder("desc.tex"))
r.stamtavle( "@I9052@", 9 )
