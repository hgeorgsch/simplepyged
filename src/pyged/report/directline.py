#16i-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Find direct line relationships via a depth first search.
"""

__all__ = [ "finddescendant", "mklines", "mkqueue" ]

from .graph import finddescendant
from . import date 
from queue import Queue

def simplename(node):
      fn = "%s %s" % node.name()
      by = node.birth_year()
      dy = node.death_year()
      if by is None and dy is None: return fn
      r = ""
      if not by is None: r += str(by)
      r += "--"
      if not dy is None: r += str(dy)
      return f"{fn} ({r})"

def mklinesaux(l,n,r):
        l.append( f"{n}. {simplename(r[0])}" )
        nx = r[1]
        if len(nx) == 0: 
            l.append("")
        for i in nx:
            mklinesaux(l,n+1,i)

def mklines(r):
   l = []
   mklinesaux(l,1,r)
   return l

def mkqueueaux(q,n,r):
   q.put( (n, r[0]) )
   nx = r[1]
   for i in nx:
      mkqueueaux(q,n+1,i)

def mkqueue(r):
    q = Queue()
    mkqueueaux(q,1,r)
    return q
