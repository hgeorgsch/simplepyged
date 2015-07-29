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

from errors import *
from records import Line

class MediaObject(Line):
    """
    A class for MultiMedia objects, whether containing text or an xref. 
    """

    def _init(self):
       self._record = None
       self._file = None
       self._title = None
       self._type = None
       v = self.value()
       self._use = False
       u = self.children_single_tag("_USE")
       if u != None and u.value().strip() == "Y":
	  self._use = True
       if valid_pointer(v):
	  self._record = self._dict.get(v)
	  if self._record == None: 
	     raise GedcomMissingRecordError, "Missing record " + v
          rec = self._record
       else:
           rec = self
       print rec
       file = rec.children_single_tag("FILE")
       self._file = file.value()
       try: 
          form = file.children_single_tag("FORM")
          self._form = form.value()
          self._type = form.children_single_tag("TYPE").value()
       except: 
          self._form = NONE
          self._type = NONE
       try:
          self._title = file.children_single_tag("TITL").value()
       except:
           self._title = None


    def get_file(self): return self._file
    def get_form(self): return self._form
    def get_use(self): return self._use
    def get_type(self): return self._type
    def get_title(self): return self._title
