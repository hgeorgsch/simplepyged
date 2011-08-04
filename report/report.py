#-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Report generators for GEDCOM files.  The implementation uses the
builder pattern with the slight modification that the builder outputs
directly to file and provides no get_result() method.

The Report class is the Director and is associated with a Gedcom object
(document) and a Builder object upon instantiation.  Different Director
methods provide different kinds of reports.

The Builder class is an abstract Builder, included primarily to serve as
a template for Concrete Builders.
"""

__all__ = [ "Report", "Builder" ]
from . import date 
from simplepyged.errors import * 


class devnull():
   def append(self,*a): pass
class unsupport():
   def append(self,e): 
      print "Warning! Unsupported tag.", e

class IndiBins(dict):
   def add(self,e):
      k = e.tag()
      if self.has_key(k): self[k].append(e)
      else: self[None].append(e)
   def __init__(self):
      # Event records
      self[None] = []
      # Other records
      self["NAME"] = []
      self["NOTE"] = []
      self["OBJE"] = []
      self["SOUR"] = []
      self["FAMS"] = []
      self["FAMC"] = []
      # Unsupported records
      self["ALIA"] = unsupport()
      # Ignore records
      self["CHAN"] = devnull()
      self["ANCI"] = devnull()
      self["DESI"] = devnull()
      self["RESN"] = devnull()
      self["RIN"]  = devnull()
      self["RFN"]  = devnull()
      self["AFN"]  = devnull()
      self["REFN"] = devnull()
      self["SUBM"] = devnull()

dic_norsk = { "and" : "og", 
              "daughter" : "dotter til", 
              "son" : "son til", 
              "child" : "barn av", 
              "born" : "fødd", 
              "died" : "død", 
              "married" : "gift", 
              "with" : "med", 
              "sources" : "kjelder", 
	    }

class Report(object):

   def __init__(self,file,builder=None,dic=dic_norsk):
      self.__file = file
      self.__history = {}
      if builder == None: self._builder = Builder()
      else: self._builder = builder
      self._dic = dic

   def citation(self,node):
      assert node.tag() == "SOUR"
      val = node.value()
      media = node.children_tags("OBJE")
      notes = node.children_tags("NOTE")
      if valid_pointer(val): 
	 source = self.__file.get(val)
	 page = node.children_single_tag("PAGE")
	 data = node.children_single_tag("DATA")
	 if data != None: quotes = data.children_tags("TEXT")
	 else: quotes = None
	 # TODO: Make the source record
      else:
	 raise NotImplementedError, "Only source records are supported."
	 quotes = node.children_tags("TEXT")
      # TODO: Make output (citation)

   def simplename(self,node):
      (f,s) = node.name()
      ref = self.__history.get( node.xref() )
      self._builder.put_name(f,s,ref)
      if ref != None: return
      by = node.birth_year()
      dy = node.birth_year()
      if by < 0 and dy < 0: return
      self._builder.put( "(" )
      if by >= 0: self._builder.put( str(by) )
      self._builder.put( "--" )
      if dy >= 0: self._builder.put( str(dy) )
      self._builder.put( ")" )

   def parents(self,node):
      father = node.father()
      mother = node.mother()
      if father == None and mother == None: return
      if node.sex() == "M": key = "son"
      elif node.sex() == "F": key = "daughter"
      else: key = "child"
      self._builder.put( " "+self._dic.get(key)+" " )
      if father != None:
	 father = self.simplename(father)
	 if mother != None: self._builder.put( " "+self._dic["and"]+" " )
      if mother != None:
	 mother = self.simplename(mother)

   def formatplace(self,plac):
      if plac == None: return ""
      if plac == "": return ""
      if plac == []: return ""
      return u"på " + ", ".join(plac)

   def spouse(self,fam,ind):
      marr = fam.marriage()
      # (1) Gift dato (etc)
      if marr == None:
	 if fam.children_count() > 0:
           self._builder.put( "Hadde barn med " )
	 else:
           self._builder.put( "Hadde eit forhold til " )
      else:
        (d,p) = marr.dateplace()
	if not (d or p):
          self._builder.put( self._dic["married"].capitalize() + " " )
          self._builder.put( self._dic["with"].capitalize() + " " )
        else:
          self._builder.put( self._dic["married"].capitalize() + " " )
          self._builder.put( date.formatdate(d) )
          self._builder.put( self.formatplace(p) )
          self._builder.put( self._dic["with"] + " " )
      # (2) Spouse name (and details)
      (fn,sn) = ind.name()
      self._builder.put_name(fn,sn)
      # (3) Family events
      # TODO: Family events

   def child(self,ind):
      assert ind.tag() == "INDI"
      # (1) NAME
      key = ind.xref()
      ref = self.__history.get(key)
      (fn,sn) = ind.name()
      self._builder.put_name(fn,sn,ref)

      # If the child has his/her own entry, we are done.
      if ref != None: return 

      # (2) BIRT
      birt = ind.birth()
      if birt != None:
        self._builder.put( self._dic["born"] + " " )
        (d,p) = birt.dateplace()
        self._builder.put( date.formatdate(d) )
        self._builder.put( self.formatplace(p) )
      # (3) DEAT
      deat = ind.death()
      if deat != None:
        self._builder.put( self._dic["died"] + " " )
        (d,p) = deat.dateplace()
        self._builder.put( date.formatdate(d) )
        self._builder.put( self.formatplace(p) )

   def vitals(self,ind):
      assert ind.tag() == "INDI"
      # (1) BIRT
      birt = ind.birth()
      if birt != None:
        self._builder.put( self._dic["born"] + " " )
        (d,p) = birt.dateplace()
        self._builder.put( date.formatdate(d) )
        self._builder.put( self.formatplace(p) )
      # (2) parents
      self.parents(ind)
      # (3) DEAT
      deat = ind.death()
      if deat != None:
        self._builder.put( self._dic["died"] + " " )
        (d,p) = deat.dateplace()
        self._builder.put( date.formatdate(d) )
        self._builder.put( self.formatplace(p) )

   def individual(self,ref,number=None):
      """
      Generate a report on a single individual with the given reference
      ref (either a xref or a refn).  If given, number is the person's
      ID number in a longer report.
      """
      # look up the person
      ind = self.__file.get(ref)
      key = ind.xref()

      # check if the person has already been included
      ref = self.__history.get(key)

      # find the name and make the header
      (fn,sn) = ind.name()
      self._builder.put_phead(fn,sn,number,ref)

      # if the person has been processed before, we are done
      if ref != None: return ref

      # otherwise, we sort all the child nodes for processing
      rec = IndiBins()
      for e in ind.children(): rec.add(e)

      # (1) Main name
      self._builder.put_name(fn,sn)

      # (2) OBJE ??
      # (3) vitals
      self.vitals(ind)
      self._builder.put_paragraph()

      # (4) biography (events)
      # (5) NOTE
      for n in ind.children_tags("NOTE"):
	 self._builder.put(n.value_cont())
	 for s in n.sources(): self.citation(s)
	 self._builder.put_paragraph()

      # (6) FAMS
      for n in ind.children_tag_records("FAMS"):
	 if ind.sex() == "M": self.spouse( n, n.wife() )
	 elif ind.sex() == "F": self.spouse( n, n.husband() )
         else: raise Exception, "Unknown gender for spouse"
	 self._builder.put_enum_s()
	 for c in n.children():
	    self._builder.put_item_s()
	    self.child(c)
	    self._builder.put_item_e()
	 self._builder.put_enum_e()
	 self._builder.put_paragraph()

      # (7) other names (with TYPE) (name pieces, ROMN and FONE ignored)
      L = list(ind.children_tags("NAME"))
      if len(L) > 1:
	 self._builder.put_subheader( "Ogso kjend som: " )
	 for node in L[1:]:
	    (f,s) = parse_name( node.value() )
	    self._builder.put_name( f,s )
	    # TODO print sources

      # (8) SOUR (with PAGE) (ignore EVEN, QUAY)
      #    NOTE (url only) -> link
      #    NOTE (other) -> footnote
      #    DATA -> deferred -> quotation
      #    OBJE ??
      L = list(ind.children_tags("SOUR"))
      if len(L) > 1:
        self._builder.put_subheader( self._dic.get("sources").capitalize() )
        for cit in L: self.citation(cit)

class Builder(object):
   def put_url(self,url,text): 
      if text == None: print "<URL:%s>" % (url,)
      else: print "%s <URL:%s>" % (text,url,)
   def put_ref(self,ref): 
      print "[%s]" % (ref,)
   def put_name(self,fn,sn,ref=None): 
      if ref == None: print "%s %s" % (fn,sn),
      else: print "%s %s (sjå %s)" % (fn,sn,ref),
   def put_phead(self,fn,sn,no,ref): 
      if ref == None: print "%s\t%s %s" % (no,fn,sn)
      else: print "%s\t%s %s (sjå %s)" % (no,fn,sn,ref)
      print 
   def put_subheader(self,header): print header + ":"
   def put_shead_s(self): print "*",
   def put_shead_e(self): print
   def put_chead_s(self): print "*",
   def put_chead_e(self): print
   def put_item_s(self): print "  + ",
   def put_item_e(self): print
   def put_enum_s(self): print
   def put_enum_e(self): print
   def put_quot_s(self): print "«",
   def put_quot_e(self): print "»"
   def put_foot_s(self): print "{",
   def put_foot_e(self): print "}"
   def put_dagger(self): print "d. "
   def put_paragraph(self): print "\n\n"
   def put(self,x): print x,
