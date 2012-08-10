#! /usr/bin/python

from simplepyged.gedcom import Gedcom
from simplepyged.mkrecords import *
from report.report import Report
from report.tex import texBuilder

g = Gedcom("alrik.ged")
ind = parse_ahnentafel("grabow",dict=g,source="@S555@",page="s. 204",subm="@X33@")

g._print( "test.ged" )
g._init()
r = Report(g,texBuilder("test.tex"))
r.stamtavle( "grabow", 9 )
