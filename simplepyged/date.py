#-*- coding: utf-8 -*-
# $Id$
#
# Gedcom 5.5.1 Date Parser
#
# Copyright (C) 2011 Hans Georg Schaathun (hg [ at ] schaathun.net)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Please see the GPL license at http://www.gnu.org/licenses/gpl.txt

"""
Classes to represent dates with all the flexibility required for
GEDCOM, including methods to parse date values from GEDCOM files.
"""

keywords = [ 
      "BET", "AND", 
      "BEF", "AFT",
      "FROM", "TO",
      "CAL", "EST", "INT",
      "(B.C.)" ]

class Date(object): 
   def __init__(self,*a): pass
   def year(self): return -1
   def gedcom(self): return ""
class DateProper(object): 
   def __init__(self,parts):
      self.BC = False
      dat = list(parts)
      if dat[-1] in [ "B.C.", "BC", "(B.C.)" ]:
         self.bc = True
         dat = dat[:-1]
      self._year = int(dat.pop())
      self.month = None
      self.day = None
      if len(dat) > 0: self.month = month_number[dat.pop().upper()]
      if len(dat) > 0: self.day = int(dat.pop())
      assert len(dat) == 0
   def gedcom(self):
      R = ""
      if self.day != None: R += unicode(self.day) + " "
      if self.month != None: R += months[self.month-1] + " "
      if self._year != None: R += unicode(self._year)
      return R

   def getDate(self): return (self._year,self.month,self.day)
   def year(self): 
      return self._year
   def isBC(self): return self.BC

class DateInterpreted(Date):
   def __init__(self,dat):
      assert dat[0] == "INT"
      raise NotImplementedError, "Interpreted dates not supported."
class DatePhrase(Date):
   def __init__(self,dat):
      self.date = dat
   def __str__(self): return self.date
   def getDate(self): return self.date
   def gedcom(self): return self.date
class DateApproximate(Date):
   def __init__(self,dat):
      assert dat[0] in [ "CAL", "EST", "ABT" ]
      self.approximation = dat[0]
      self.date = makeDate( dat[1:] )
   def getDate(self): return self.date
   def year(self): return self.date.year()
class DateRange(Date):
   def getDate(self): return (self.start,self.end)
   def __init__(self,dat):
      assert dat[0] in [ "BET", "BEF", "AFT" ]
      self.start = None
      self.end   = None
      if dat[0] == "BEF": self.start = makeDate( dat[1:] )
      if dat[0] == "AFT": self.end   = makeDate( dat[1:] )
      if dat[0] == "BET":
	 idx = dat.index("AND")
	 self.start = makeDate( dat[1:idx] )
	 self.end   = makeDate( dat[idx+1:] )
class DatePeriod(Date):
   def getDate(self): return (self.start,self.end)
   def __init__(self,dat):
      assert dat[0] in [ "FROM", "TO" ]
      if dat[0] == "FROM":
	 try:
	    idx = dat.index("TO")
	    self.start = makeDate( dat[1:idx] )
	    self.end   = makeDate( dat[idx+1:] )
	 except ValueError:
	    self.start = makeDate( dat[1:] )
	    self.end   = None
      else:
	 self.end   = makeDate( dat[1:] )
	 self.start = None

def makeDate(dat):
   if isinstance(dat,str): parts = dat.split()
   elif isinstance(dat,unicode): parts = dat.split()
   else: parts = dat
   if parts[0] in [ "FROM", "TO" ]: return DatePeriod( parts )
   if parts[0] in [ "CAL", "EST", "ABT" ]: return DateApproximate( parts )
   if parts[0] in [ "BET", "BEF", "AFT" ]: return DateRange( parts )
   if parts[0] == "INT": return DateInterpreted( parts )
   try:
      return DateProper( parts )
   except:
     return DatePhrase( parts )

months = [ "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
           "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", ]


month_number = {
      "JAN" : 1, "FEB" : 2, "MAR" : 3, "APR" : 4,
      "MAY" : 5, "JUN" : 6, "JUL" : 7, "AUG" : 8,
      "SEP" : 9, "OCT" : 10, "NOV" : 11, "DEC" : 12,
      }

month_nor = {
      "JAN" : "januar", "FEB" : "februar", "MAR" : "mars",
      "APR" : "april", "MAY" : "mai", "JUN" : "juni",
      "JUL" : "juli", "AUG" : "august", "SEP" : "september",
      "OCT" : "oktober", "NOV" : "november", "DEC" : "desember",
      }

