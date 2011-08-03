#! /usr/bin/python

from simplepyged.gedcom import Gedcom
from report.report import Report

g = Gedcom("alrik.ged")
r = Report(g)
r.individual("@I166@")
