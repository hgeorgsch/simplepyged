#! /usr/bin/python
#-*- coding: utf-8 -*-

import unittest
import os
from simplepyged.date import *
from report.date import *

class WrightTest(unittest.TestCase):
    """Unit tests for records.py using wright.ged."""

    def setUp(self):
       pass

    def test_exact(self):
        d1 = makeDate( "1922" )
        self.assertEqual( type(d1), DateProper )
        self.assertEqual( formatdate(d1), "1922" )

        d2 = makeDate( "0064" )
        self.assertEqual( type(d2), DateProper )
        self.assertEqual( formatdate(d2), "64" )
	      
	d1 = makeDate( "12 MAY 1777" )
        self.assertEqual( type(d1), DateProper )
        self.assertEqual( formatdate(d1), "12. mai 1777" )

        self.assertEqual(
	      formatdate(makeDate( "28 FEB 1777" )), "28. februar 1777" )
        self.assertEqual(
	      formatdate(makeDate( "5 NOV 1888" )), "5. november 1888" )
        self.assertEqual(
	      formatdate(makeDate( "1 JAN 1999" )),
	      "1. januar 1999" )

    def test_period(self):
        self.assertEqual(
	      formatdate(makeDate( "FROM 2 APR 1922" )),
	      "frå 2. april 1922" )
        self.assertEqual(
	      formatdate(makeDate( "TO 12 AUG 1944" )),
	      "til 12. august 1944" )
        self.assertEqual(
	      formatdate(makeDate( "FROM 1777 TO OCT 1779" )),
	      "1777--oktober 1779" )

    def test_range(self):
        self.assertEqual(
	      formatdate(makeDate( "BET MAR 1655 AND JUL 1655" )),
	      "mellom mars 1655 og juli 1655" )
        self.assertEqual(
	      formatdate(makeDate( "BEF JUL 1450" )),
	      "før juli 1450" )
        self.assertEqual(
	      formatdate(makeDate( "AFT JUN 1512" )),
	      "etter juni 1512" )

    def test_dates(self):
        self.assertEqual(
	      formatdate(makeDate( "ABT 1777" )), "omkring 1777" )
        self.assertEqual(
	      formatdate(makeDate( "FROM ABT 1777 TO 2 SEP 1790" )),
	      "omkring 1777--2. september 1790" )

if __name__ == '__main__':
    unittest.main()
