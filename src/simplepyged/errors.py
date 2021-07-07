#-*- coding: utf-8 -*-
#
# Gedcom 5.5 Parser
#
# Copyright (C) 2011 Hans Georg Schaathun (hg [ at ] schaathun.net)
# Copyright (C) 2010 Nikola Škorić (nskoric [ at ] gmail.com)
# Copyright (C) 2005 Daniel Zappala (zappala [ at ] cs.byu.edu)
# Copyright (C) 2005 Brigham Young University
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
#
# To contact the author, see http://github.com/dijxtra/simplepyged

# __all__ = [ "GedcomParseError" ]

"""
This module contains all the Exception classes and functions for
error handling and error checking for all the other submodules
of the package.
"""

# Functions for error checking

def valid_pointer(st):
    s = st.strip()
    if len(s) < 3: return False
    else: return s[0] == "@" and s[-1] == "@"

# Exception classes

class GedcomParseError(Exception):
    """ Exception raised when a Gedcom parsing error occurs
    """
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value

class MalformedPointerError(Exception): 
   """
   Exception to be raised when what should be an xref pointer
   does not fit the required syntax.
   """
   pass
class GedcomMissingRecordError(Exception): 
   """
   Exception to be raised when an xref pointer points to 
   a non-existent record.
   """
   pass
class GedcomStructureError(Exception):
   """
   Exception to be raised when structural inconsistencies are found
   in the Gedcom data structure, e.g. a family CHIL pointer without
   an inverse.
   """
   pass
