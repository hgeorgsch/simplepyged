#! /usr/bin/python

from simplepyged.gedcom import Gedcom
from simplepyged.mkrecords import *
from report.report import Report
from report.tex import texBuilder

g = Gedcom("alrik.ged")

g._print( "test.ged" )
g._init()
r = Report(g,texBuilder("inger.tex"))
r.stamtavle( "@I8251@", 9 )
