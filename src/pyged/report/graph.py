#-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Graph generators for GEDCOM files.
"""

__all__ = [ "Graph" ]
from . import date 
from .report import devnull, unsupport, IndiBins, dic_norsk, Builder
from pyged.gedcom.errors import * 
from pyged.gedcom.events import Event
from queue import Queue

from functools import reduce

def pedigree(file,ref1,ngen=4):
      "Find direct descendance from one individual to another."
      # Setup
      ind1 = file.get( ref1 )
      assert ind1 != None, "Root person not found."
      return mkpedigree(ind1,ngen)
def mkpedigree(ind1,ngen):
   if ngen == 1:
       return (ind1,[])
   else:
       r = []
       if ind1.father(): r.append(ind1.father())
       if ind1.mother(): r.append(ind1.mother())
       return (ind1,[mkpedigree(c,ngen-1) for c in r ])
def descendants(file,ref1,ngen=4):
      "Find direct descendance from one individual to another."
      # Setup
      ind1 = file.get( ref1 )
      assert ind1 != None, "Root person not found."
      return mkdescendants(ind1,ngen)
def mkdescendants(ind1,ngen):
   if ngen == 1:
       return (ind1,[])
   else:
       return (ind1,[mkdescendants(c,ngen-1) for c in ind1.children() ])


def finddescendant(file,ref1,ref2):
      "Find direct descendance from one individual to another."
      # Setup
      ind1 = file.get( ref1 )
      assert ind1 != None, "Root person not found."
      ind2 = file.get( ref2 )
      assert ind2 != None, "Target person not found."
      return depthfirst(file,ind1,ind2)
def depthfirst(file,ind1,ind2):
   r = [] ;
   for c in ind1.children():
       if c == ind2:
           r = [(c,[])]
       else:
           a = depthfirst(file,c,ind2) 
           if a != None:
               r.append(a)
   if r == []: return None
   else: 
       return (ind1,r)

def unfoldgraph(g,p=[]):
    print( "g", type(g) )
    if isinstance(g,tuple): return unfoldgraph([g])
    if g == []:
        return [p]
    else:
        b = [ unfoldgraph( s, p+[c] ) for (c,s) in g ]
        print( "b", b )
        b = reduce( lambda x,y : x+y, b, [] )
        return b
# unfoldgraph( [ (0,[(1,[]),(2,[(4,[]),(5,[(6,[]),(7,[])]),(3,[])])])  ] )


graphpreamble = (u"\\documentclass[10pt]{standalone}\n"
              + u"\\usepackage{tikz}\n"
              + u"\\usepackage{luatex85}\n"
              + u"\\usetikzlibrary{graphs,graphdrawing,quotes}\n"
              + u"\\usegdlibrary{force}\n"
              + u"\\usegdlibrary{layered}\n"
              + u"\\def\\nodebox{\\parbox{24mm}}\n"
              + u"\\begin{document}\n\\tiny\n"
              + u"  \\begin{tikzpicture}\n")
graphpostamble = u"  \\end{tikzpicture}\n\\end{document}\n"
figurepreamble = (u"\\begin{tikzpicture}\n")
figurepostamble = u"\\end{tikzpicture}\n"

def buildchildren(b,gs,edge="->"):
    q = Queue()
    d = dict()
    cdict = dict()
    q.put( (1,gs) )
    root = gs[0]
    while not q.empty():
       (n,gs) = q.get(False)
       cl = gs[1]
       if cl:
          p = gs[0]
          if not cdict.get(p,False):
              cdict[p] = True
              putnode(b,p) 
              b.put( " " + edge + " { " ) 
              for c in cl:
                    putnode(b,c[0]) 
                    b.put( ", " )
                    q.put((n+1,c)) 
              b.put( " }, \n " ) 

def buildtree(b,gs,edge="->"):
    """
    This does not work.
    It is a dropin replacement for buildchildren(), aiming
    to reduce the number of crossing edges, but the attempt fails,
    and we get more arrows pointing upwards.
    """
    ss = unfoldgraph(gs)
    for path in ss:
        cnt = False
        for node in path:
            if cnt:
                b.put( "\n " + edge + " " ) 
            cnt = True
            putnode(b,node) 
        b.put( ",\n " ) 

def putnode(b,node):
      b.put( '"\\nodebox{\\raggedright ' ) 
      (f,s) = node.name()
      b.put_name(f,s)
      by = node.birth_year()
      dy = node.death_year()
      if not (by is None and dy is None): 
         r = "("
         if not by is None: r += str(by)
         r += "--" 
         if not dy is None: r += str(dy)
         b.put( r + ")" )
      b.put( ' }" ' ) 

class Graph(object):
   __indicontext = True

   def __init__(self,file,builder=None,dic=dic_norsk,figure=False):
      self.__file = file
      self.__reflist = set()
      self.__context = []
      if builder == None: self._builder = Builder()
      else: self._builder = builder
      self._dic = dic
      if figure:
          self._postamble = figurepostamble
          self._preamble = figurepreamble
      else:
          self._postamble = graphpostamble
          self._preamble = graphpreamble

   def mkgraph(self,ref1,ref2,header=None,abstract=None):
      "Generate a graph of individuals."
      gs = finddescendant( self.__file, ref1, ref2 )
      if gs is None:
          raise Exception( "No descendants found" )
      self.printgraph(gs,header,abstract)

   def printgraph(self,gs,header=None,abstract=None,grow="down",edge="->"):
      self._builder.preamble( preamble=self._preamble )
      self._builder.put( "\\tikzstyle{every node}=[fill=blue!10,opacity=50]\n" )
      self._builder.put( "\\graph[layered layout,grow=" + grow + "] {\n" )
      buildchildren(self._builder,gs,edge)

      # Tail matter
      self._builder.put( "}; \n" )
      self._builder.postamble(self._postamble)

   def mkdescendants(self,ref1,ngen=4,header=None,abstract=None):
      "Generate a graph of individuals."
      gs = descendants( self.__file, ref1, ngen )
      self.printgraph(gs,header,abstract)
   def mkpedigree(self,ref1,ngen=4,header=None,abstract=None):
      "Generate a graph of individuals."
      gs = pedigree( self.__file, ref1, ngen )
      self.printgraph(gs,header,abstract,grow="right",edge="<-")
