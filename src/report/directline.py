#-*- coding: utf-8 -*-
# $Id: report.py 768 2011-08-01 19:09:45Z georg $

"""
Find direct line relationships via a depth first search.
"""

__all__ = [ "finddescendant" ]
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
   for c in ind1.children():
       if c === ind2:
           r = [c]
       else:
           r = [x for x in depthfirst(file,c,ind2) if x != None ]
   if r = []: return None
   else: return (c,r)
