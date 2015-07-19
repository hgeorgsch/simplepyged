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
   """
   A pseudo-list object, implementing the append() method, but
   does nothing, simply ignoring the data.
   """
   def append(self,*a): pass
class unsupport():
   """
   A pseudo-list object, similar to the devnull class.
   It implements the append() method, and will issue a warning
   whenever an object is appended, but otherwise ignore the data.
   """
   def append(self,e): 
      print "Warning! Unsupported tag.", e

class IndiBins(dict):
   def add(self,e):
      k = e.tag()
      if self.has_key(k): self[k].append(e)
      else: self[None].append(e)
   def __init__(self,ind=None):
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
      if ind != None:
         for e in ind.children_lines(): self.add(e)

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
              "CENS" : "registrert i folketeljing", 
              "EMIG" : "utvandra", 
              "IMMI" : "innvandra", 
              "RESI" : u"busett", 
              "DEAT" : u"død", 
              "BURI" : "gravlagd", 
              "PROB" : "skifte", 
              "PROP" : u"åtte", 
	    }

class Report(object):
   __indicontext = True

   def __init__(self,file,builder=None,dic=dic_norsk):
      self.__file = file
      self.__history = {}
      self.__reflist = set()
      self.__context = []
      if builder == None: self._builder = Builder()
      else: self._builder = builder
      self._dic = dic

   def history_add(self,ind,no):
      """
      Record the given individual ind as included in the report under
      Entry no.
      """
      key = ind.xref()
      refno = self.__history.get( key )
      if refno == None: self.__history[key] = no
      return self.__history[key] 

   # String formatting

   def formatplace(self,plac):
      """
      Format the given place plac, specified as a list of strings,
      and return a single string for printout.  No text is actually
      printed from this method.  If the place name is missing, 
      an empty string is returned.
      """
      # For a missing place, plac could be either None, "", or [].
      # The following conditional captures all of them, returning
      # an empty string for a missing place.
      if not plac: return ""
      return " " + plac.text(prep=True,local=self.__context)
      #return u" på " + ", ".join(plac)

   # Output production methods

   def stamtavle(self,ref,mgen=12,header=None,abstract=None):
      "Generate a detailed ahnentafel report."
      q = Queue()
      ind = self.__file.get( ref )
      if header == None:
	 header = "Stamtavle for %s %s" % ind.name()
      self._builder.preamble( header )
      if abstract != None:
        self._builder.put_abstract_s( )
        self._builder.put( abstract )
        self._builder.put_abstract_e( )
      assert ind != None
      q.put( ( 1, 1, ind ) )
      self.history_add(ind,1)
      pgen = 0
      while not q.empty():
	 (cgen, no, ind ) = q.get(False)
	 if pgen < cgen:
	    self._builder.put_shead( "Generasjon " + str(cgen) )
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
      self.make_reflist()
      self._builder.postamble()
   def descendants(self,ref,mgen=12,header=None,abstract=None):
      "Generate a detailed report of descendants of the given individual."
      # Setup
      q = Queue()
      ind = self.__file.get( ref )
      assert ind != None, "Root person not found."
      q.put( ( 1, 1, ind ) )
      self.history_add(ind,1)
      pgen = 0
      # Header and abstract
      if header == None:
	 header = u"Etterkomarane åt %s %s" % ind.name()
      self._builder.preamble( header )
      if abstract != None:
        self._builder.put_abstract_s( )
        self._builder.put( abstract )
        self._builder.put_abstract_e( )
      # Main loop
      while not q.empty():
	 (cgen, no, ind ) = q.get(False)
	 if pgen < cgen:
	    self._builder.put_shead( "Generasjon " + str(cgen) )
	    pgen = cgen
	 cno = no
	 for c in ind.children():
	    if c.children_count() == 0: continue
	    cno += 1
	    q.put( ( cgen+1, cno, c ) )
            self.history_add(c,cno)
	 self.individual(ind=ind,number=no)
      # Tail matter
      self.make_reflist()
      self._builder.postamble()
   def make_reflist(self):
      for s in self.__reflist:
	 if s == None:
	    print self
	    print self.__reflist
	    raise Exception, "None occurs in reference list."
	 author = s.children_single_val( "AUTH" )
	 title  = s.children_single_val( "TITL" )
	 url    = None
	 pub    = s.children_single_val( "PUBL" )
	 notes  = None
	 xref   = s.xref()
	 self._builder.put_bib( xref, author, title, url, pub, notes )
      return

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
	 else: self._builder.put( type )
      elif tag == "PROP":
         tx = self._dic.get(tag,tag)
         self._builder.put( tx )
	 self._builder.put( val )
      elif tag == "OCCU":
	 self._builder.put( val )
      else:
         tx = self._dic.get(tag,tag)
         self._builder.put( tx )
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
      if not ( d or p ): self._builder.put( " " )
      self._builder.put( self.formatplace( p ) )
      # NOTE/SOUR/OBJE
      noteq = []
      for n in event.children_tags("NOTE"):
	 if n.note_type() == "prose":
	    noteq.append(n)
	 else:
	    self._builder.put(n.value_cont())
	    for s in n.sources(): self.citation(s)
      # TODO distinguish between different kinds of notes.
      for n in event.children_tags("SOUR"):
	 self.citation( n )
      self._builder.end_sentence( )
      if noteq:
         self._builder.end_period( )
	 for n in noteq:
	    self._builder.put(n.value_cont())
	    for s in n.sources(): self.citation(s)
         self._builder.end_period("")
         
      # TODO clean up presentation of sources
      # TODO OBJE
      # Finalise

   def citation(self,node):
      """
      Process a source citation structure and produce appropriate
      report output.
      """
      assert node.tag() == "SOUR"
      val = node.value()
      media = node.children_tags("OBJE")
      notes = node.children_tags("NOTE")
      if valid_pointer(val): 
	 source = self.__file.get(val)
	 if source == None:
	    print node.gedcom()
	    raise Exception, "Source was not found."
	 page = node.children_single_tag("PAGE")
	 if page != None: page = page.value()
	 data = node.children_single_tag("DATA")
	 if data != None: quotes = data.children_tags("TEXT")
	 else: quotes = None
	 self.__reflist.add( source )
	 self._builder.put_cite( val, page )
	 # TODO: handle notes and quotes
      else:
	 if node.is_empty():
	    print "Warning!  Empty source citation"
	    return
	 else:
	    print node.gedcom()
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

   def spouse(self,fam,ind,short=False):
      marr = fam.marriage()
      # Different cases.
      # 1.  Spouse and children.
      #     Gift med ... Born:
      #     Hadde born med ... (:)
      # 2.  Spouse with no children
      #     Gift med ... 
      #     Hadde eit forhold til ...
      # 3.  Married with children, unknown spouse.
      #     Gift (...) Born:
      # 4.  Married w/o children, unknown spouse.
      #     Gift (...) Born:
      # 5.  Children.  Unknown partner.
      #     Born:
      # 6.  One-person family with non-marriage events only.
      #     Family.
      # 7.  One-person family with no information.  Error?
      #     -
      #     print error/warning
      # (1) Gift dato (etc)
      if marr == None:
	 if fam.children_count() > 0:
           self._builder.put( "Hadde barn med " )
	 else:
           self._builder.put( "Hadde eit forhold til " )
      else:
        (d,p) = marr.dateplace()
	if not (d or p):
          self._builder.put( self._dic["married"] + " " )
        else:
          self._builder.put( self._dic["married"] + " " )
          self._builder.put( date.formatdate(d) )
	  if d != None and p != None: self._builder.put( " " )
          self._builder.put( self.formatplace(p) )
      # (2) Spouse name (and details)
      if ind != None:
        self._builder.put( " " + self._dic["with"] + " " )
        (fn,sn) = ind.name()
	ref = self.__history.get(ind.xref())
        self._builder.put_name(fn,sn,ref)
	if ref != None and short: 
            self._builder.end_period()
            return
      self._builder.end_period()
      # (3) Family events
      # TODO: Family events
      # TODO: Family sources

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
        self._builder.put( " " + self._dic["born"] + " " )
        (d,p) = birt.dateplace()
        self._builder.put( date.formatdate(d) )
        self._builder.put( self.formatplace(p) )
      # (3) DEAT
      deat = ind.death()
      if deat != None:
        self._builder.put( " " + self._dic["died"] + " " )
        (d,p) = deat.dateplace()
        self._builder.put( date.formatdate(d) )
        self._builder.put( self.formatplace(p) )
      # (4) DEAT
      for n in ind.children_tag_records("FAMS"):
	 if ind.sex() == "M": spouse = n.wife()
	 elif ind.sex() == "F": spouse = n.husband() 
	 if spouse == None: continue
	 self._builder.put( "g.m. " ) 
	 self._builder.put( " ".join(spouse.name()) ) 
	 self._builder.put( "; " ) 

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
      self._builder.end_period()
      # (3) DEAT
      deat = ind.death()
      if deat != None:
        self._builder.put( " " + self._dic["died"] + " " )
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
      if self.__indicontext:
	 self.__context = []


      # check if the person has already been included
      ref = self.__history.get(key)
      if ref != None and ref < number:
          (fn,sn) = ind.name()
          self._builder.put_phead_repeat(fn,sn,number,ref)
          return ref
      else:
          # Make a complete new entry
          return self.new_individual(ind,ref)

   def new_individual(self,ind,number):
      """
      Generate a report on a single individual object ind, 
      where number is the person's ID number in a longer report.
      """

      (fn,sn) = ind.name()
      self._builder.put_phead(fn,sn,number,ind.xref())

      # We sort all the child nodes for processing
      rec = IndiBins(ind)

      # (1) Main name
      self._builder.put_name(fn,sn)
      self._builder.end_sentence()

      # (2) OBJE ??
      for obj in rec["OBJE"]:
          if obj.get_type() != "photo": continue
          t = obj.get_title()
          f = obj.get_file()
          print t
          print f
          if not t: t = ""
          self._builder.put_image(t,f)

      # (3) vitals (birth and parents)
      birt = ind.birth()
      if birt != None: self.event( ind, birt )
      self.parents( ind )
      self._builder.end_period()
      deat = ind.death()
      if deat != None: self.event( ind, deat )
      self._builder.end_period()
      self._builder.end_paragraph()

      # (4) biography (events)
      for e in rec[None]:
	 if e.tag() == "BIRT": continue
	 elif e.tag() == "DEAT": continue
	 else: self.event( ind, Event( e ) )
      #self.vitals(ind)
      # CHR
      # other
      # DEAT 
      # BURI 
      # PROB
      self._builder.end_period()
      self._builder.end_paragraph()

      # (5) NOTE
      for n in ind.children_tags("NOTE"):
	 self._builder.put(n.value_cont())
	 for s in n.sources(): self.citation(s)
	 self._builder.end_paragraph()

      # (6) FAMS
      for n in ind.children_tag_records("FAMS"):
	 if ind.sex() == "M": spouse = n.wife()
	 elif ind.sex() == "F": spouse = n.husband() 
         else: 
	    print "Warning! Unknown gender for individual", ind.xref()
	    spouse = n.wife()
	    if spouse == ind: spouse = n.husband() 
	 short = False
	 if spouse != None:
           sref = self.__history.get( spouse.xref() )
	   if sref != None and sref < number: short = True
	 self.spouse( n, spouse, short )
	 if short: continue
         cc = n.children_count_exact()
         # TODO: Check examples
         # TODO: -> Discuss missing children in records
	 cs = list(n.children())
         if cc:
             print "NCHI: ", cc
             if len(cs) > cc:
                 print "Warning! Inconsistency.  Too many children recorded."
             if cc == 0:
               self._builder.put( "Dei hadde ingen born\n" )
               self._builder.end_period()
             elif len(cs) > 0:
               self._builder.put( "Dei hadde " + str(cc) + " born:\n" )
             else:
               self._builder.put( "Dei hadde " + str(cc) + " born" )
               self._builder.end_period()
         else:
             self._builder.put( "Born:" )
	 if len(cs) > 0:
	   self._builder.put_enum_s()
	   for c in cs:
	      self._builder.put_item_s()
	      self.child(c)
	      self._builder.put_item_e()
	   self._builder.put_enum_e()
	 self._builder.end_paragraph()

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
      if len(L) > 0:
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
   def put_shead(self,title=""): print "* " + title + "\n"
   def put_chead(self,title=""): print "*" + title + "\n"
   def put_item_s(self): print "  + ",
   def put_item_e(self): print
   def put_enum_s(self): print
   def put_enum_e(self): print
   def put_quot_s(self): print "«",
   def put_quot_e(self): print "»"
   def put_foot_s(self): print "{",
   def put_foot_e(self): print "}"
   def put_dagger(self): print "d. "
   def end_paragraph(self): print "\n\n"
   def end_period(self): print ".  "
   def end_sentence(self): print ", "
   def put(self,x): print x,
   def preamble(self): pass
   def postamble(self): pass
   def put_bib( self, xref, author, title, url, publication, notes ):
     pass
