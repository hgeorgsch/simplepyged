#16i-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Find direct line relationships via a depth first search.
"""

__all__ = [ "finddescendant", "printline", "mklines" ]
from . import date 

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

def printlineaux(n,r):
    if len(r) == 0: 
        print "No line found"
    else:
        print u"" + unicode(n) + u". " + simplename(r[0]) 
        nx = r[1]
        if len(nx) > 0: 
           printlineaux(n+1,nx[0])

        if len(nx) > 1: 
            print
            for i in nx[1:]:
                 printlineaux(n+1,i)

def printline(r):
    return printlineaux(1,r)
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
