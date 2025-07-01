#-*- coding: utf-8 -*-
# $Id$
#
# Gedcom 5.5.1 Date Parser
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
This module provides the single :func:`formatdate` which takes a 
:class:`Date` object to return a human readable string.
"""

__all__ = [ "formatdate" ]

from pyged.gedcom.date import *

def formatdate(dat,space=True):
   if dat == None: return ""
   elif dat == "": return ""
   elif isinstance(dat,DateApproximate):
      return " omkring " + formatdate( dat.getDate() )
   elif isinstance(dat,DateRange):
      (d1,d2) = dat.getDate()
      if d2 == None: return u"før " + formatdate(d1)
      elif d1 == None: return u"etter " + formatdate(d2)
      else: return u" mellom " + formatdate(d1) + " og " + formatdate(d2)
   elif isinstance(dat,DatePeriod):
      (d1,d2) = dat.getDate()
      if d2 == None: return u" frå " + formatdate(d1)
      elif d1 == None: return u" til " + formatdate(d2)
      else: return formatdate(d1) + "--" + formatdate(d2,space=False)
   elif isinstance(dat,DatePhrase):
      return str(dat)
   else:
      (y,m,d) = dat.getDate()
      if space:
         R = u" "
      else:
         R = u""
      if d != None: R += str(d) + ". "
      if m != None: R += month_norsk[m] + " "
      R += str(y)
      if dat.isBC(): R += " f.Kr."
      return R

month_norsk = {
      1 : "januar", 2 : "februar", 3: "mars",
      4 : "april",  5 : "mai",     6 : "juni",
      7 : "juli",   8 : "august",  9 : "september",
      10 : "oktober", 11 : "november", 12 : "desember",
      }

