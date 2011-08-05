#-*- coding: utf-8 -*-
#
# Gedcom 5.5 Parser
#
# Copyright (C) 2011 Hans Georg Schaathun (hg [ at ] schaathun.net)
# Copyright (C) 2010 Nikola Škorić (nskoric [ at ] gmail.com)
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

import date

# Global imports
class Event(object):
    """ Class represeting an event """
    def __init__(self, line):
        self.line = line

        self.type = self._get_value('TYPE')
        self.date = self._get_value('DATE')
	if ( self.date != None): self.date = date.makeDate( self.date )
        self.place = self._get_value('PLAC')
	if ( self.place != None):
	   self.place = [ p.strip() for p in self.place.split( "," ) ]

    def tag(self): return self.line.tag()
    def value(self): return self.line.value()
    def children_single_tag(self,*a,**kw):
       return self.line.children_single_tag(*a,**kw)
    def year(self):
       if self.date == None: R = -1
       else: R = self.date.year()
       return R

    def _get_value(self, tag):
        """ Returns value of a child tag"""
        C = self.line.children_single_tag(tag)
	if C == None: return None
	else: return C.value()
        
    def dateplace(self):
        """ Returns a pair of strings in format (date, place) """
        date = ''
        place = ''

        if self.date != None:
            date = self.date
        if self.place != None:
            place = self.place

        return (date, place)

# text TYPE/event CAUS AGE ved AGNC, DATE på/i PLAC
# NOTE/SOUR/OBJE

# TYPE
# DATE/PLAC
# AGE
# CAUS/AGNC
# NOTE/SOUR/OBJE
# Ignore: RESN/RELI/ADDR
