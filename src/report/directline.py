#16i-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Find direct line relationships via a depth first search.
"""

__all__ = [ "finddescendant", "mklines", "mkqueue" ]
from graph import finddescendant
from . import date 
from Queue import Queue

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

def simplename(node):
      fn = u"%s %s" % node.name()
      by = node.birth_year()
      dy = node.death_year()
      if by < 0 and dy < 0: return fn
      r = ""
      if by >= 0: r += unicode(by)
      r += "--"
      if dy >= 0: r += unicode(dy)
      return unicode(fn + u" (" + r + u")")

def mklinesaux(l,n,r):
        l.append( u"" + unicode(n) + u". " + simplename(r[0]) )
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
