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

from .errors import *
from .records import Line
from .notes import valid_url

class MediaObject(Line):
    """
    A class for MultiMedia objects, whether containing text or an xref. 
    """

    def __init__(self,*a,**kw):
       Line.__init__(self,*a,**kw)
       self._record = None
       self._file = None
       self._title = None
       self._type = None

    def _init(self):
       v = self.value()
       u = self.children_single_tag("_USE")
       if u == None: 
           self._use = None
       elif u.value().strip() == "Y":
           self._use = True
       else:
           self._use = False
       if valid_pointer(v):
          self._record = self._dict.get(v)
          if self._record == None: 
             raise GedcomMissingRecordError( "Missing record " + v )
          rec = self._record
       else:
           rec = self
       print(rec)
       fs = list(rec.children_tags("FILE"))
       if len(fs) == 0:
          raise Exception( "Media object with no file given" )
       if len(fs) > 1:
          print("Warning: Media object with multiple files is not supported.")
       file = fs[0]
       self._file = file.value()
       try: 
          form = file.children_single_tag("FORM")
          self._form = form.value()
          self._type = form.children_single_tag("TYPE").value()
       except: 
          self._form = None
          self._type = None
       try:
          self._title = file.children_single_tag("TITL").value()
       except:
           self._title = None


    # Comment out the following to avoid printing the xref
    # when outputting gedcom
    ## def xref(self): 
       ## if self._record: return self._record.xref()
       ## else: return None
    def is_url(self): 
       return valid_url(self._file)
    def get_url(self):
       if self.is_url(): return self._file
       else: return None
    def get_file(self): return self._file
    def get_form(self): return self._form
    def get_use(self): 
       if self._use == None:
          return (self.get_type() == "photo")
       else:
          return self._use
    def get_type(self): return self._type
    def get_title(self): return self._title
