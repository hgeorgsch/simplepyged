#-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Graph generators for GEDCOM files.
"""

__all__ = [ "Graph" ]
from . import date 
from report import devnull, unsupport, IndiBins, dic_norsk, Builder
from directline import finddescendant
from simplepyged.errors import * 
from simplepyged.events import Event
from simplepyged.records import parse_name

from Queue import Queue


graphpreamble = (u"\\documentclass[10pt]{standalone}\n"
              + u"\\usepackage{tikz}\n"
              + u"\\usepackage{luatex85}\n"
              + u"\\usetikzlibrary{graphs,graphdrawing,quotes}\n"
              + u"\\usegdlibrary{force}\n"
              + u"\\usegdlibrary{layered}\n"
              + u"\\begin{document}\n\\tiny\n"
              + u"  \\begin{tikzpicture}\n")
graphpostamble = u"  \\end{tikzpicture}\n\\end{document}\n"

def buildchildren(b,gs):
    q = Queue()
    d = dict()
    q.put( (1,gs) )
    root = gs[0]
    while not q.empty():
       (n,gs) = q.get(False)
       if gs[1]:
          p = gs[0]
          putnode(b,p) 
          cl = gs[1]
          if len(cl) == 1:
             c = cl[0]
             b.put( " ->  [orient=down] " )
             putnode(b,c[0]) 
             b.put( ",\n " ) 
             q.put((n+1,c)) 
             d[c[0]] = max(d.get(c[0],0),n+1)
          else:
             b.put( " -> { " ) 
             for c in cl:
                putnode(b,c[0]) 
                b.put( ", " )
                q.put((n+1,c)) 
                d[c[0]] = max(d.get(c[0],0),n+1)
             b.put( " }, \n " ) 
    putsamelayer(b,root,d)

def putsamelayer(b,root,d):
    l = dict()
    for k in d.keys():
        v = d[k]
        l[v] = l.get(v,[])
        l[v].append( k )
    maxl = 0
    for k in l.keys():
        if maxl < k: maxl = k
        b.put( " { [same layer] " ) 
        for n in l[k]:
           print k, n.name()
           putnode(b,n)
           b.put( ", " ) 
        b.put( " }; " ) 
        b.put_comment( k ) 


def putnode(b,node):
      print node.name()
      b.put( '"\\parbox{24mm}{\\raggedright ' ) 
      (f,s) = node.name()
      b.put_name(f,s)
      by = node.birth_year()
      dy = node.death_year()
      if not (by < 0 and dy < 0): 
         r = "("
         if by >= 0: r +=str(by)
         r += "--" 
         if dy >= 0: r += str(dy) 
         b.put( r + ")" )
      b.put( ' }" ' ) 

class Graph(object):
   __indicontext = True

   def __init__(self,file,builder=None,dic=dic_norsk):
      self.__file = file
      self.__reflist = set()
      self.__context = []
      if builder == None: self._builder = Builder()
      else: self._builder = builder
      self._dic = dic

   def mkgraph(self,ref1,ref2,header=None,abstract=None):
      "Generate a graph of individuals."
      gs = finddescendant( self.__file, ref1, ref2 )

      self._builder.preamble( preamble=graphpreamble )
      self._builder.put( "\\tikzstyle{every node}=[fill=blue!10,opacity=50]\n" )
      self._builder.put( "\\graph[,layered layout,grow=down] {\n" )
      buildchildren(self._builder,gs)

      # Tail matter
      self._builder.put( "}; \n" )
      self._builder.postamble(graphpostamble)

