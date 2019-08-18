#-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Graph generators for GEDCOM files.
"""

__all__ = [ "Graph" ]
from . import date 
from report import devnull, unsupport, IndiBins, dic_norsk, Builder
from directline import finddescendant, mkgq
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
       a = finddescendant( self.__file, ref1, ref2 )
       q = mkgq(a)
       self.mkgraphaux(q,header,abstract)
   def mkgraphaux(self,q,header=None,abstract=None):
      "Generate a report of a given list (queue) of individuals."

      no = 0
      ln = 999999

      self._builder.preamble( preamble=graphpreamble )
      self._builder.put( "\\graph[layered layout,grow down,node distance=20mm] {\n" )

      # Main loop
      while not q.empty():
          pn = ln
	  (ln, ind ) = q.get(False)
          no += 1
          print no, ln, ind.name()
          if ln <= pn:
              self._builder.put( ",\n" ) 
          else:
              self._builder.put( " -> " ) 
          self._builder.put( '"\\parbox{25mm}{' ) 
          self.simplename(ind) 
          self._builder.put( '}"' ) 

      # Tail matter
      self._builder.put( "}; \n" )
      self._builder.postamble(graphpostamble)

   def simplename(self,node):
      (f,s) = node.name()
      self._builder.put_name(f,s)
      by = node.birth_year()
      dy = node.death_year()
      if by < 0 and dy < 0: return
      r = "("
      if by >= 0: r +=str(by)
      r += "--" 
      if dy >= 0: r += str(dy) 
      self._builder.put( r + ")" )

