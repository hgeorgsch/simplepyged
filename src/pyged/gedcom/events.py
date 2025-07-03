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

"""
This module provides the Event class to handle event structures 
in Gedcom.
"""

from . import date
from .place import Place

class Event(object):
    """
    Class represeting an event.

    Note that this class is totally incompatible with the Gedcom
    Node or Line classes.  This is not satisfactory, and this class
    should be redesigned to implement the same interface, either by
    subclassing or by implementing the Decorator pattern.

    A few essential methods() are provided as a partial implementation
    of a Decorator pattern, as they have been required by other 
    packages.
    """
    def __init__(self, line):
        self.line = line

        self.type = self.children_single_val('TYPE')
        self.date = self.children_single_val('DATE')
        if ( self.date != None): self.date = date.makeDate( self.date )
        self.place = Place.get( self.children_single_val('PLAC') )
        #if ( self.place != None):
           #self.place = [ p.strip() for p in self.place.split( "," ) ]

    def __lt__(self,other):
        if other == None: return False
        elif self.date == None: return False
        elif other.date == None: return False
        else: return self.date.__lt__(other.date)
    def __gt__(self,other):
        if other == None: return False
        elif self.date == None: return False
        elif other.date == None: return False
        else: return self.date.__gt__(other.date)
    def __eq__(self,other):
        if other == None: return False
        elif self.date == None: return False
        elif other.date == None: return False
        else: return self.date.__eq__(other.date)
    def __le__(self,other):
       return self.__lt__(other) or self.__eq__(other)
    def __ge__(self,other):
       return self.__gt__(other) or self.__eq__(other)
    # The following methods partially implement a Decorator pattern
    def tag(self):
       return self.line.tag()
    def value(self):
       return self.line.value()
    def children_tags(self,*a,**kw):
       return self.line.children_tags(*a,**kw)
    def children_single_tag(self,*a,**kw):
       return self.line.children_single_tag(*a,**kw)
    def children_single_val(self, tag):
        """ Returns value of a child tag"""
        return self.line.children_single_val(tag)

    # Other methods
    def year(self):
       if self.date == None: R = None
       else: R = self.date.year
       return R

    def dateplace(self):
        """
        Returns a pair (date, place), where Date is a Date object
        and place is a list of strings.
        """
        date = ''
        place = ''

        if self.date != None:   date = self.date
        if self.place != None:  place = self.place

        return (date, place)

# text TYPE/event CAUS AGE ved AGNC, DATE på/i PLAC
# NOTE/SOUR/OBJE

# TYPE
# DATE/PLAC
# AGE
# CAUS/AGNC
# NOTE/SOUR/OBJE
# Ignore: RESN/RELI/ADDR
