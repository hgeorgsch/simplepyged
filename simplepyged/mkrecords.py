#-*- coding: utf-8 -*-
#
# Gedcom 5.5 Parser
#
# Copyright (C) 2011 Hans Georg Schaathun (hg [ at ] schaathun.net)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Please see the GPL license at http://www.gnu.org/licenses/gpl.txt

from .records import *
import codecs

def newIndividual(name,dict,source,page=None,gender="U",dead=True,subm=None):
   """
   Create a new individual with specified name, source citation
   and submitter reference.
   """
   ind = Individual( level=0, xref=None, tag="INDI", value=None, dict=dict )
   nam = Line( level=1, xref=None, tag="NAME", value=name, dict=dict )
   ind.add_child_line( nam )
   ind.add_child_line( Line( level=1, xref=None, tag="SEX", value=gender, dict=dict) )
   if dead:
     ind.add_child_line( Line( level=1, xref=None, tag="DEAT", value="Y", dict=dict ) )
   if subm:
     ind.add_child_line( Line( level=1, xref=None, tag="SUBM", value=subm, dict=dict) )
   src = Line( level=1, xref=None, tag="SOUR", value=source, dict=dict )
   ind.add_child_line( src )
   if page:
      src.add_child_line( Line( level=2, xref=None, tag="PAGE", value=page, dict=dict ) )
   dict.add_record(ind)
   return ind

def parse_ahnen_line(line,dict,source,page=None,dead=True,subm=None):
   """
   Parse a single line from a simple text file ahnentafel.
   This is an auxiliary for parse_ahnentafel().
   """
   (no,line) = line.split(".")
   no = int(no)
   if no == 1: gender = "U"
   elif no % 2 == 0: gender = "M"
   elif no % 2 == 1: gender = "F"
   try:
     (name,line) = line.split(";")
   except ValueError:
      name = line
      line = None
   name = name.strip()
   if line != None:
     line = line.strip()
     assert line[0] == "("
     assert line[-1] == ")"
     (b,d) = line[1:-1].split("-")
   else:
      (b,d) = ("","")
   ind = newIndividual(name,dict,source,page,gender=gender,dead=False,subm=subm)
   if b != "":
      e = Line(1,None,"BIRT",None,dict)
      e.add_child_line( Line(2,None,"DATE",b,dict) )
      ind.add_child_line( e )
   if d != "":
      e = Line(1,None,"DEAT",None,dict)
      e.add_child_line( Line(2,None,"DATE",d,dict) )
      ind.add_child_line( e )
   elif dead:
      e = Line(1,None,"DEAT","Y",dict)
      ind.add_child_line( e )
   return (no,ind)

def parse_ahnentafel(file,*a,**kw):
   """
   Parse a text file in a simple ahnentafel format and
   create a dict of Individual objects, keyed by the individual's
   (integer) number in the ahnentafel.
   """
   # Find a way to use an existing entry for the first individual
   f = codecs.open( file, "r", "UTF-8" )
   newdict = {}
   for l in f:
      if l.strip() == "": continue
      (no,ind) = parse_ahnen_line(l,*a,**kw)
      newdict[no] = ind
   f.close()
   mkfam(newdict)
   return newdict[1]

def mkfam(newdict):
   for k in newdict.keys():
      ind = newdict[k]
      f = newdict.get(2*k)
      m = newdict.get(2*k+1)
      if not ( f or m ): continue
      ind.add_parents( f, m )
      # TODO: make sure that the source is recorded in the family as well