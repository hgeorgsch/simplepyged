#-*- coding: utf-8 -*-
# $Id$
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

import codecs

from .errors import *
from .records import Line

def valid_url(s):
   t = s.strip()
   if len(t.split()) > 1: return False
   if t[:7] == "http://": return True
   if t[:8] == "https://": return True
   if t[:6] == "ftp://": return True
   return False

class NoteStructure(Line):
    """
    A class for note structures, whether containing text or an xref. 
    """

    def _init(self):
       self._record = None
       self._type = None
       v = self.value()
       if valid_pointer(v):
          self._record = self._dict.get(v)
          if self._record == None: 
             raise GedcomMissingRecordError( "Missing record " + v )

    def gettext(self):
        """Return the text of the note, whether it is inline or from an
        associated record."""
        if self._record:
            return self._record.value_cont()
        else:
            return self.value_cont()

    def sources(self):
       """
       Return an iterator of all sources associated with the note.
       """
       L = list( self.children_tags("SOUR") )
       if len(L) > 0: 
          print("Warning!  Sources attached to Note Structures is not valid GEDCOM")
          print(str(self))
       if self._record != None:
          if len(L) > 0: 
             print("Sources in note structure are ignored.  Move them to source record")
          return self._record.children_tags("SOUR")
       else:
          return L

    def note_type(self):
        """
        Return the contents type of note, identifying a few special 
        cases like a URL only.
        """
        if self._type == None:
           v = self.value_cont()
           s = v.strip()
           if valid_url(v): self._type = "url"
           elif s[0].islower() and s[-1] != ".": self._type = "phrase"
           else: self._type = "prose"
        return self._type
