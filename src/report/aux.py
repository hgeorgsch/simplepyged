#-*- coding: utf-8 -*-

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
      print("Warning! Unsupported tag.", e)

def formatPageElement( p ):
   l = [ x.strip() for x in p.split(":") ]
   if len(l) == 1: return l[0]
   if len(l) != 2: raise Exception( "Malformed page reference (" + p + ")." )
   if l[0] == "page": return "s. " + l[1]
   elif l[0] == "number": return "nr. " + l[1]
   elif l[0] == "entry": return "oppslag " + l[1]
   elif l[0] == "list": return "liste " + l[1]
   elif l[0] == "street": return l[1]
   return l[0] + " " + l[1]
def formatPage( p ):
   return [ formatPageElement(x) for x in p.split(",") ]

class IndiBins(dict):
   def add(self,e):
      k = e.tag()
      if k in self: self[k].append(e)
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
      self["ASSO"] = []
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
              "associates" : "andre relevante personar", 
              "sources" : "kjelder", 
              "BIRT" : u"fødd", 
              "CHR" : u"døypt", 
              "BAPM" : u"døypt", 
              "CONF" : "konfirmert", 
              "GRAD" : "eksamen", 
              "OCCU" : "yrke", 
              "CENS" : "registrert i folketeljing", 
              "EMIG" : "utvandra", 
              "IMMI" : "innvandra", 
              "RESI" : u"busett", 
              "RETI" : u"pensjonert", 
              "DEAT" : u"død", 
              "BURI" : "gravlagd", 
              "PROB" : "skifte", 
              "PROP" : u"åtte", 
	    }
