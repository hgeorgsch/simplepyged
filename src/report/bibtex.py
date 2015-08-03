#-*- coding: utf-8 -*-
# $Id$

import bibtexparser as bp

class BibEntry(dict):
   def __init__(self,id,type="misc"):
      if isinstance(id,str):
         self["id"] = id
         self["type"] = type
      else:
	 self.update(id)
   def set(self,key,value):
      self[key] = value
   def provide(self,key,value):
      if not self.has_key(key): self[key] = value
   def append(self,key,value):
      if not self.has_key(key): self[key] = value
      else: self[key] += " " + value

class BibDatabase(bp.bibdatabase.BibDatabase):
    def __init__(self,db=None):
         bp.bibdatabase.BibDatabase.__init__(self)
	 if db != None:
	    self.entries = [ BibEntry(x) for x in db.entries ]
            self._entries_dict = db._entries_dict 
            self.comments = db.comments
            self.strings = db.comments
            self.preambles = db.preambles
    def add(self,entry):
       if not isinstance(entry,BibEntry): entry = BibEntry(entry)
       self.entries.append(entry)
def loads(*a,**kw):
   db = bp.loads(*a,**kw)
   return BibDatabase(db)
def load(*a,**kw):
   db = bp.load(*a,**kw)
   return BibDatabase(db)

dump = bp.dump
dumps = bp.dumps

