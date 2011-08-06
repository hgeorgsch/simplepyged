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
from simplepyged.events import Event
from simplepyged.records import parse_name

from Queue import Queue

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
      # ignored records (handled elsewhere)
      self["SEX"] = devnull()

dic_norsk = { "and" : "og", 
              "daughter" : "dotter til", 
              "son" : "son til", 
              "child" : "barn av", 
              "born" : u"fødd", 
              "died" : u"død", 
              "married" : "gift", 
              "with" : "med", 
              "sources" : "kjelder", 
              "BIRT" : u"fødd", 
              "CHR" : u"døypt", 
              "GRAD" : "eksamen", 
              "OCCU" : "yrke", 
              "CENS" : "folketeljing", 
              "EMIG" : "utvandra", 
              "IMMI" : "innvandra", 
              "RESI" : u"busett", 
              "DEAT" : u"død", 
              "BURI" : "gravlagd", 
              "PROB" : "skifte", 
	    }

class Report(object):

   def __init__(self,file,builder=None,dic=dic_norsk):
      self.__file = file
      self.__history = {}
      self.__reflist = []
      if builder == None: self._builder = Builder()
      else: self._builder = builder
      self._dic = dic

   def history_add(self,ind,no):
      key = ind.xref()
      refno = self.__history.get( key )
      if refno == None: self.__history[key] = no
      return self.__history[key] 

   def stamtavle(self,ref,mgen=12,header="Stamtavle"):
      self._builder.preamble( header )
      q = Queue()
      ind = self.__file.get( ref )
      assert ind != None
      q.put( ( 1, 1, ind ) )
      self.history_add(ind,1)
      pgen = 0
      while not q.empty():
	 (cgen, no, ind ) = q.get(False)
	 if pgen < cgen:
	    self._builder.put_shead_s()
	    self._builder.put( "Generasjon " + str(cgen) )
	    self._builder.put_shead_e()
	    pgen = cgen
	 if cgen < mgen:
           f = ind.father()
	   if f != None: 
	      q.put( ( cgen+1, 2*no, f ) )
              self.history_add(f,2*no)
           m = ind.mother()
	   if m != None: 
	      q.put( ( cgen+1, 2*no + 1, m ) )
              self.history_add(m,2*no + 1)
	 self.individual(ind=ind,number=no)
      self._builder.postamble()
   def event(self,ind,event):
      # text TYPE/event CAUS AGE ved AGNC, DATE på/i PLAC
      # NOTE/SOUR/OBJE
      tag    = event.tag()
      val    = event.value()
      type   = event.children_single_tag("TYPE")
      if type != None: type   = type.value()
      gender = ind.sex()
      # TYPE/event
      if tag == "EVEN":
	 if type == None: self._builder.put( "EVEN" )
	 else: self._builder.put( type.capitalize() )

      elif tag == "OCCU":
	 self._builder.put( val.capitalize() )
      else:
         self._builder.put( self._dic.get(tag,tag).capitalize() )
	 if type != None: self._builder.put( "(" + type + ")" )
      self._builder.put( " " )
      # CAUS
      c = event.children_single_tag("CAUS")
      if c != None: self._builder.put( "av " + c.value() )
      # AGE
      c = event.children_single_tag("AGE")
      if c != None: self._builder.put( "(" + c.value() + ")" )
      # AGNC
      c = event.children_single_tag("AGNC")
      if c != None:
	 self._builder.put( "ved " + c.value() )
      # DATE/PLAC:
      (d,p) = event.dateplace()
      self._builder.put( date.formatdate( d ) )
      if d != None and p != None: self._builder.put( " " )
      self._builder.put( self.formatplace( p ) )
      # Finalise
      self._builder.put( ". " )
      # NOTE/SOUR/OBJE
      for n in event.children_tags("NOTE"):
	 self._builder.put(n.value_cont())
	 for s in n.sources(): self.citation(s)
      # TODO distinguish between different kinds of notes.
      # TODO SOUR/OBJE
   def citation(self,node):
      assert node.tag() == "SOUR"
      val = node.value()
      media = node.children_tags("OBJE")
      notes = node.children_tags("NOTE")
      if valid_pointer(val): 
	 source = self.__file.get(val)
	 page = node.children_single_tag("PAGE")
	 if page != None: page = page.value()
	 data = node.children_single_tag("DATA")
	 if data != None: quotes = data.children_tags("TEXT")
	 else: quotes = None
	 self.__reflist.append( source )
	 self._builder.put_cite( val, page )
	 # TODO: handle notes and quotes
	 # TODO: process reference list
      else:
	 raise NotImplementedError, "Only source records are supported."
	 quotes = node.children_tags("TEXT")

   def simplename(self,node):
      (f,s) = node.name()
      ref = self.__history.get( node.xref() )
      self._builder.put_name(f,s,ref)
      if ref != None: return
      by = node.birth_year()
      dy = node.death_year()
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
      self._builder.put( ". " )

   def formatplace(self,plac):
      if plac == None: return ""
      if plac == "": return ""
      if plac == []: return ""
      return u"på " + ", ".join(plac)

   def spouse(self,fam,ind,short=False):
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
        else:
          self._builder.put( self._dic["married"].capitalize() + " " )
          self._builder.put( date.formatdate(d) )
	  if d != None and p != None: self._builder.put( " " )
          self._builder.put( self.formatplace(p) )
      # (2) Spouse name (and details)
      if ind != None:
        self._builder.put( " " + self._dic["with"] + " " )
        (fn,sn) = ind.name()
	ref = self.__history.get(ind.xref())
        self._builder.put_name(fn,sn,ref)
	if ref != None and short: return
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

   def individual(self,ref=None,number=None,ind=None):
      """
      Generate a report on a single individual with the given reference
      ref (either a xref or a refn).  If given, number is the person's
      ID number in a longer report.
      """
      # look up the person
      if ind == None: ind = self.__file.get(ref)
      key = ind.xref()

      # check if the person has already been included
      ref = self.__history.get(key)

      # find the name and make the header
      (fn,sn) = ind.name()
      if ref != None and ref < number:
	 self._builder.put_phead_repeat(fn,sn,number,ref)
      else:
	 self._builder.put_phead(fn,sn,number,key)

      # if the person has been processed before, we are done
      if ref != None and ref < number: return ref

      # otherwise, we sort all the child nodes for processing
      rec = IndiBins()
      for e in ind.children_lines(): rec.add(e)

      # (1) Main name
      self._builder.put_name(fn,sn)
      self._builder.put( " " )

      # (2) OBJE ??
      # (3) vitals (birth and parents)
      birt = ind.birth()
      if birt != None: self.event( ind, birt )
      self.parents( ind )

      # (4) biography (events)
      for e in rec[None]:
	 if e.tag() == "BIRT": continue
	 else: self.event( ind, Event( e ) )
      #self.vitals(ind)
      # CHR
      # other
      # DEAT 
      # BURI 
      # PROB
      self._builder.put_paragraph()

      # (5) NOTE
      for n in ind.children_tags("NOTE"):
	 self._builder.put(n.value_cont())
	 self._builder.put( "---" )
	 for s in n.sources(): self.citation(s)
	 self._builder.put_paragraph()

      # (6) FAMS
      for n in ind.children_tag_records("FAMS"):
	 if ind.sex() == "M": spouse = n.wife()
	 elif ind.sex() == "F": spouse = n.husband() 
         else: 
	    print "Warning! Unknown gender for individual", key
	    spouse = n.wife()
	    if spouse == ind: spouse = n.husband() 
	 short = False
	 if spouse != None:
           sref = self.__history.get( spouse.xref() )
	   if sref < ref: short = True
	 self.spouse( n, spouse, short )
	 if short: return
	 cs = list(n.children())
	 if len(cs) > 0:
	   self._builder.put_enum_s()
	   for c in cs:
	      self._builder.put_item_s()
	      self.child(c)
	      self._builder.put_item_e()
	   self._builder.put_enum_e()
	 self._builder.put_paragraph()

      # (7) other names (with TYPE) (name pieces, ROMN and FONE ignored)
      L = list(ind.children_tags("NAME"))
      if len(L) > 1:
	 self._builder.put_subheader( "Ogso kjend som: " )
	 for node in L[1:-1]:
	    (f,s) = parse_name( node )
	    self._builder.put_name( f,s )
	    self._builder.put( ", " )
	    # TODO print sources
	 (f,s) = parse_name( L[-1] )
	 self._builder.put_name( f,s )

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
   def put_url(self,url,text=None): 
      if text == None: print "<URL:%s>" % (url,)
      else: print "%s <URL:%s>" % (text,url,)
   def put_cite(self,ref): 
      print "[%s]" % (ref,)
   def put_name(self,fn,sn,ref=None): 
      if ref == None: print "%s %s" % (fn,sn),
      else: print "%s %s (sjå %s)" % (fn,sn,ref),
   def put_phead(self,fn,sn,no,key): 
      print "%s\t%s %s" % (no,fn,sn)
      print
   def put_phead_repeat(self,fn,sn,no,ref): 
      print "%s\t%s %s (sjå %s)" % (no,fn,sn,ref)
      print 
   def put_subheader(self,header): print header + ":"
   def put_book_title(self,h): print " ###    %s    ### " % (h,)
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
   def preamble(self): pass
   def postamble(self): pass
