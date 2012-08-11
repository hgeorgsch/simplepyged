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

"""
Adding records to a Gedcom file.

The functions of this module are intended to provide a simple API
to add individuals and families to a Gedcom file.

It is under construction and will need some refactoring before the
documentation is presented.
"""

# TODO: set CHAN structure

from .records import *
import codecs

def mkcitation(source,page=None,level=1,dict=None):
   src = Line( level=level, xref=None, tag="SOUR", value=source, dict=dict )
   if page:
      src.add_child_line( Line( level=level+1, xref=None, tag="PAGE", value=page, dict=dict ) )
   return src

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
   ind.add_child_line( mkcitation( source, page, dict=dict ) )
   dict.add_record(ind)
   return ind

def parse_individual(line,dict,source,page=None,dead=True,subm=None,gender="U"):
   """
   Parse the main part of a single line from simple person description.
   This is an auxiliary for line parsers.
   """
   if line[0] == ">":
      ref = line[1:].strip() 
      ind = dict.get( ref ) 
      print ref
      print ind
      return ind
   L = line.split(";")
   name = L[0].strip()
   L = L[1:]
   (b,d) = ("","")
   E = []
   ref = None
   for line in L:
      line = line.strip()
      if line == "": continue
      if line[0] == "(":
         assert line[-1] == ")"
         (b,d) = line[1:-1].split("-")
      elif line[0] == "<": # REFN
	 if ref != None:
	    raise ValueError, "Only one REFN per individual is supported."
	 ref = line[1:].strip()
         E.append( Line(1,None,"REFN",ref,dict) )
         if self._record_dict.has_key(ref):
	    raise Exception, "Record with same REFN already exists"
      elif line[0] == "(": # gender
	 l = line[1:].strip()
	 gender = l[0]
      else: # NOTE
         E.append( Line(1,None,"NOTE",line,dict) )
   ind = newIndividual(name,dict,source,page,gender=gender,dead=False,subm=subm)
   if ref != None:
      dict._record_dict[ref] = ind
   for e in E:
      ind.add_child_line( e )
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
   return ind

def parse_desc(file,dict,source,*a,**kw):
   f = codecs.open( file, "r", "UTF-8" )
   L = [ l.split(".",1) for l in f ]
   f.close()
   fam = None
   last = None
   for (no,line) in L:
      if no == "g":
	 # Get date of marriage
	 (md,line) = line.split(";",1)
	 md = md.strip()
	 line = line.strip()
      ind = parse_line(line,dict,source,*a,**kw)
      if no == "":
         # Make family with father
         last = None
      elif no == "gm" or no == "g":
	 if last == None:
            # Add individual as spouse
	    fam.add_spouse(ind)
	 else:
	    # make new family with spouse
	    pass
         last = None
      else:
         # Add individual as child
         fam.add_child(ind)
         last = ind

def parse_ahnen_line(line,dict,source,*a,**kw):
   """
   Parse a single line from a simple text file ahnentafel.
   This is an auxiliary for parse_ahnentafel().
   """
   (no,line) = line.split(".")
   line = line.strip()
   no = int(no)
   if no == 1: gender = "U"
   elif no % 2 == 0: gender = "M"
   elif no % 2 == 1: gender = "F"
   kw["gender"] = gender
   ind = parse_individual(line,dict,source,*a,**kw)
   return (no,ind)

def parse_ahnentafel(file,*a,**kw):
   """
   Parse a text file in a simple ahnentafel format and
   create a dict of Individual objects, keyed by the individual's
   (integer) number in the ahnentafel.
   """
   f = codecs.open( file, "r", "UTF-8" )
   newdict = {}
   for l in f:
      if l.strip() == "": continue
      (no,ind) = parse_ahnen_line(l,*a,**kw)
      newdict[no] = ind
   f.close()
   if not kw.has_key("page"): kw["page"] = None
   mkfam(newdict,source=kw["source"],page=kw["page"],dict=kw["dict"])
   return newdict[1]

def mkfam(newdict,source=None,page=None,dict=None):
   """
   Create the new families required by an ahnentafel.
   This is an auxiliary function for parse_ahnentafel()
   """
   for k in newdict.keys():
      ind = newdict[k]
      f = newdict.get(2*k)
      m = newdict.get(2*k+1)
      if not ( f or m ): continue
      fam = ind.add_parents( f, m )
      fam.add_child_line( mkcitation( source, page, dict=dict ) )
      # TODO: make sure that the source is recorded in the family as well
