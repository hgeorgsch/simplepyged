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

prepList = [ "i", "i", "i", "i",
            "i", "i", "på", "på", ]

def parsePlace(s):
   raise NotImplementedError

class Place(object):
   countries = {}
   def __init__(self,s):
      if isinstance(s,name,parent=None,short=None):
	 s = parsePlace(s)
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
	 yield L.pop().getName()
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
      return bool(self.name)
   def getAName(self):
      """Get the base name of the place, or the parent place if
      no name is defined."""
      if self.isNone(): 
	 return self.parent.getAName()
      else: 
	 return self.getName()
   def text(self,local=[]):
      "Return the full name as it should be written in prose."
      if self.short != None:
	 return self.short
      elif self.parent == None:
	 return self.getName()
      elif self.isNone():
	 return self.parent.text(local)
      elif self in local:
	 return self.getName()
      elif self.getName() == self.parent.getAName():
	 return self.parent.text(local)
      else:
	 return self.parent.text(local) + ", " + self.getName()
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
      if isinstance(s,str):
	 s = parsePlace(s)
      c = s[0]
      if cls.countries.has_key(c):
	 P = cls.countries[c]
      else:
	 P = cls( [c] )
	 cls.countries[c] = P
      return P.getPlace( s[1:] )
   def getPlace(self,s):
      """Get or create a Place object  for the place defined by s,
      as descendant of self, which may be a string as it is taken 
      from GEDCOM or a list of strings."""
      if len(s) == 0:
	 return self
      c = s[0]
      if self.children.has_key(c):
	 P = self.children[c]
      else:
	 P = Place( [c], parent=self )
	 self.children[c] = P
      return P.getPlace( s[1:] )

for (s,p) in defaults:
   P = Place.get(p)
   P.setShort(s)
