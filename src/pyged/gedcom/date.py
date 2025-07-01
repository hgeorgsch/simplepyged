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

Different classes are used for the different types of dates, such as
approximate dates, periods, imparsable date phrases, and exact dates.
The Date class is the common ancestor of all the classes.

Normally, the makeDate() function should be used to create new Date
objects.  It takes the value from a gedcom DATE field as input, 
and instantiates an object of the most appropriate class. 
"""

### keywords = [ "BET", "AND", "BEF", "AFT", "FROM", "TO",
###       "CAL", "EST", "INT", "(B.C.)" ]

class Date(object): 
   "Superclass for all the different date classes in the module."
   def __init__(self,*a): 
      self.year = None
      self.month = None
      self.day = None
   def gedcom(self):
      """
      Return a value string in valid Gedcom format so that it can
      be written to file.
      """
      return ""
   def refdate(self):
       return self
   def __lt__(self,other):
       date0 = self.refdate()
       try:
          date1 = other.refdate()
       except:
           return False
       if date0.year == None: return False
       if date1.year == None: return False
       if date0.year < date1.year: return True
       if date0.year > date1.year: return False
       if date0.month == None: return False
       if date1.month == None: return False
       if date0.month < date1.month: return True
       if date0.month > date1.month: return False
       if date0.day == None: return False
       if date1.day == None: return False
       if date0.day < date1.day: return True
       if date0.day > date1.day: return False
       return False
   def __gt__(self,other):
       date0 = self.refdate()
       try:
          date1 = other.refdate()
       except:
           return False
       if date0.year == None: return False
       if date1.year == None: return False
       if date0.year < date1.year: return False
       if date0.year > date1.year: return True
       if date0.month == None: return False
       if date1.month == None: return False
       if date0.month < date1.month: return False
       if date0.month > date1.month: return True
       if date0.day == None: return False
       if date1.day == None: return False
       if date0.day < date1.day: return False
       if date0.day > date1.day: return True
       return False
   def __eq__(self,other):
       date0 = self.refdate()
       try:
          date1 = other.refdate()
       except:
           return False
       if date0.year == None: return False
       if date1.year == None: return False
       if date0.year != date1.year: return False
       if date0.month == None: return True
       if date1.month == None: return True
       if date0.month != date1.month: return False
       if date0.day == None: return True
       if date1.day == None: return True
       if date0.day != date1.day: return False
       return True
   def __le__(self,other):
       return self.__lt__(other) or self.__eq__(other)
   def __ge__(self,other):
       return self.__gt__(other) or self.__eq__(other)
class DateProper(Date): 
   def __init__(self,parts):
      super(DateProper,self).__init__()
      self.BC = False
      dat = list(parts)
      if dat[-1] in [ "B.C.", "BC", "(B.C.)" ]:
         self.bc = True
         dat = dat[:-1]
      self.year = int(dat.pop())
      if len(dat) > 0: self.month = month_number[dat.pop().upper()]
      if len(dat) > 0: self.day = int(dat.pop())
      assert len(dat) == 0
   def gedcom(self):
      R = ""
      if self.day != None: R += self.day + " "
      if self.month != None: R += months[self.month-1] + " "
      if self.year != None: R += self.year
      return R

   def getDate(self): return (self.year,self.month,self.day)
   def isBC(self): return self.BC

class DateInterpreted(Date):
   def __init__(self,dat):
      super(DateInterpreted,self).__init__()
      assert dat[0] == "INT"
      raise NotImplementedError( "Interpreted dates not supported." )
class DatePhrase(Date):
   def __init__(self,dat):
      super(DatePhrase,self).__init__()
      self.date = dat
   def __str__(self): return " ".join(self.date)
   def getDate(self): return self.date
   def gedcom(self): return self.date
class DateApproximate(Date):
   """
   An approximate date, as defined in Gedcom by the CAL, EST, and ABT
   keywords.
   """
   def __init__(self,dat):
      super(DateApproximate,self).__init__()
      assert dat[0] in [ "CAL", "EST", "ABT" ]
      self.approximation = dat[0]
      self.date = makeDate( dat[1:] )
   def getDate(self): return self.date
class DateInterval(Date):
   def getDate(self): return (self.start,self.end)
   def refdate(self): 
       if self.start != None: return self.start
       else: return self.end
class DateRange(DateInterval):
   """
   A date approximated by a range, as defined in Gedcom by the
   BET/AND, BEF, and AFT keywords.
   """
   def refdate(self): 
       if self.start != None: return self.start
       else: return self.end
   def __init__(self,dat):
      super(DateRange,self).__init__()
      assert dat[0] in [ "BET", "BEF", "AFT" ]
      self.start = None
      self.end   = None
      if dat[0] == "BEF": self.start = makeDate( dat[1:] )
      if dat[0] == "AFT": self.end   = makeDate( dat[1:] )
      if dat[0] == "BET":
         idx = dat.index("AND")
         self.start = makeDate( dat[1:idx] )
         self.end   = makeDate( dat[idx+1:] )
class DatePeriod(DateInterval):
   """
   A date period, as defined in Gedcom by the FROM and TO keywords.
   """
   def __init__(self,dat):
      super(DatePeriod,self).__init__()
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
   """
   Instantiate an object of an appropriate class by parsing the
   given string dat, which should be a valid Gedcom date value.
   """
   if isinstance(dat,str): parts = dat.split()
   # elif isinstance(dat,unicode): parts = dat.split()
   else: parts = dat
   if len(parts) == 0: return None
   if parts[0] in [ "FROM", "TO" ]: return DatePeriod( parts )
   if parts[0] in [ "CAL", "EST", "ABT" ]: return DateApproximate( parts )
   if parts[0] in [ "BET", "BEF", "AFT" ]: return DateRange( parts )
   if parts[0] == "INT": return DateInterpreted( parts )
   try:
      return DateProper( parts )
   except:
     return DatePhrase( parts )

# The following two dictionaries are used to parse and write
# Gedcom date values.
months = [ "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
           "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", ]
month_number = {
      "JAN" : 1, "FEB" : 2, "MAR" : 3, "APR" : 4,
      "MAY" : 5, "JUN" : 6, "JUL" : 7, "AUG" : 8,
      "SEP" : 9, "OCT" : 10, "NOV" : 11, "DEC" : 12,
      }

# The following dictionary is not used here.
# TODO: see if it can be moved to the report package

month_nor = {
      "JAN" : "januar", "FEB" : "februar", "MAR" : "mars",
      "APR" : "april", "MAY" : "mai", "JUN" : "juni",
      "JUL" : "juli", "AUG" : "august", "SEP" : "september",
      "OCT" : "oktober", "NOV" : "november", "DEC" : "desember",
      }

