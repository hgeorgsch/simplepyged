#-*- coding: utf-8 -*-
# $Id$

# Omit local context

defaults = [
      ( "Ålesund", ( "Ålesund", "Sunnmøre", "", "Norge" ) ),
      ( "Ålesund", ( "Ålesund", "Møre og Romsdal", "", "Norge" ) ),
      ( "Bergen", ( "Bergen", "Hordaland", "", "Norge" ) ),
      ( "Bergen", ( "Bergen", "", "", "Norge" ) ),
      ( "Kjøbenhavn", ( "Kjøbenhavn", "", "", "Danmark" ) ),
      ( "Kristiansund N", ( "Kristiansund N", "Nordmøre", "", "Norge" ) ),
      ( "Trondheim", ( "Trondhjem", "Sør-Trøndelag", "", "Norge" ) ),
      ( "Trondheim", ( "Trondhjem", "", "", "Norge" ) ),
      ( "Trondheim", ( "Trondheim", "Sør-Trøndelag", "", "Norge" ) ),
      ( "Kristiansand S", ( "Kristiansand S", "Vest-Agder", "", "Norge" ) ),
      ( "Hordaland", ( "Hordaland", "", "Norge" ) ),
      ( "Sunnmøre", ( "Sunnmøre", "", "Norge" ) ),
      ( "Møre og Romsdal", ( "Møre og Romsdal", "", "Norge" ) ),
      ]

prepList = [ u"i", u"i", u"i", u"i",
            u"i", u"i", u"på", u"på", 
            u"i", ]

def parsePlace(s):
   if s == None:
      return None
   elif s == "":
      return []
   else:
      r = [ p.strip() for p in s.split( u"," ) ]
      return r

class Place(object):
   countries = {}
   def __init__(self,name,parent=None,short=None):
      self.name = name
      self.children = {}
      self.parent = parent
      self.short = short
   def __iter__(self):
      P = self
      L = [ ]
      while P != None:
         L.append(P)
         P = P.parent
      while len(L) > 0:
         y = L.pop().getName()
         yield y
   def getName(self):
      "Return the base name of the place as a string."
      if self.name:
         return self.name
      else:
         return ""
   def asList(self):
      "Return the full hierarchical name of the place as a list of strings."
      if self.parent == None:
         R = []
      else:
         R = self.parent.asList()
      R.append(self.getName())
      return R
   def gedcom(self):
      "Return the name of the place as it is to be written in GEDCOM."
      return ", ".join(self.asList())
   def isNone(self):
      "Return False if there is no name at this level."
      return not bool(self.name)
   def getAName(self):
      """Get the base name of the place, or the parent place if
      no name is defined."""
      if self.isNone(): 
         if self.parent == None:
            return ""
         else:
            return self.parent.getAName()
      else: 
         return self.getName()
   def text(self,prep=False,local=[]):
      "Return the full name as it should be written in prose."
      if local == None:
         local = []
      if self.short != None:
         R = self.short
      elif self.parent == None:
         R = self.getName()
      elif self.isNone():
         R = self.parent.text(local=local)
      elif self in local:
         R = self.getName()
      else:
         local.append(self)
         if self.getName() == self.parent.getAName():
            R = self.parent.text(local=local)
         else:
            R = self.getName() + ", " + self.parent.text(local=local)
      if prep:
         return self.preposition() + " " + R
      else:
         return R
   def setShort(self,short):
      self.short = short
   def level(self):
      if self.parent == None:
         return 0
      else:
         return 1 + self.parent.level()
   def preposition(self,lang=prepList):
      return lang[self.level()]
   @classmethod
   def get(cls,s):
      """Get or create a Place object for the place defined by s,
      which may be a string as it is taken from GEDCOM or a list
      of strings."""
      if s == None:
         return None
      # if isinstance(s,str):
      #    s = unicode(s)
      # if isinstance(s,unicode):
      #    s = parsePlace(s)
      if isinstance(s,str):
         s = parsePlace(s)
      if not s:
         return None
      c = s[-1]
      if c in cls.countries:
         P = cls.countries[c]
      else:
         P = cls( c )
         cls.countries[c] = P
      return P.getPlace( s[:-1] )
   def getPlace(self,s):
      """Get or create a Place object  for the place defined by s,
      as descendant of self, which may be a string as it is taken 
      from GEDCOM or a list of strings."""
      if len(s) == 0:
         return self
      c = s[-1]
      if c in self.children:
         P = self.children[c]
      else:
         P = Place( c, parent=self )
         self.children[c] = P
      return P.getPlace( s[:-1] )

for (s,p) in defaults:
   P = Place.get(p)
   P.setShort(s)
