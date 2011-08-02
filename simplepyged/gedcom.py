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

# __all__ = ["Gedcom", "Line", "GedcomParseError"]

# Global imports
import string
import codecs
from records import *
from errors import *
from traceback import print_exc

def parse_line(line):
  line = line.strip("\r\n")
  level,rest = line.split(" ",1)
  level = int(level)
  if level < 0: raise RuntimeError, "Line must start with a positive integer"

  if rest[0] == "@":
     pointer,rest = rest.split("@ ",1)
     pointer += "@"
     if not valid_pointer(pointer):
        raise MalformedPointerError, "Malformed pointer"
  else:
     pointer = ""

  try:
    tag,value = rest.split(" ",1)
  except ValueError as e:
     tag = rest
     value = ""

  return (level,pointer,tag,value)

class Gedcom(Node):
    """ Gedcom parser

    This parser is for the Gedcom 5.5 format.  For documentation of
    this format, see

    http://homepages.rootsweb.com/~pmcbride/gedcom/55gctoc.htm

    This parser reads a GEDCOM file and parses it into a set of lines.
    These lines can be accessed via a list (the order of the list is
    the same as the order of the lines in the GEDCOM file), or a
    dictionary (only lines that represent records: the key to the
    dictionary is a unique identifier of each record).

    """

    def __init__(self,file):
        """ Initialize a Gedcom parser. You must supply a Gedcom file.
        """
	Node.__init__(self)
        self._record_dict = {}
        self._current_level = -1
        self._current_line = self
        self._individuals = 0
        self._parse(file)

    def record_dict(self):
        """ Return a dictionary of records from the Gedcom file.  Only
        records that have xref defined are listed in the dictionary.
        The key for the dictionary is the xref.
        """
        return self._record_dict

    def individual_list(self):
        """ Return a list of all the individuals in the Gedcom file.  The
        individuals are in the same order as they appeared in the file.
        """
        return self.children_tags("INDI")

    def family_list(self):
        """ Return a list of all the families in the Gedcom file.  The
        families are in the same order as they appeared in the file.
        """
        return self.children_tags("FAM")

    def get_record(self, xref):
        """ Return an object of class Record (or it's subclass) identified by xref """
        return self.record_dict()[xref]

    def get_individual(self, xref):
        """ Return an object of class Individual identified by xref """
        record = self.get_record(xref)
        if record.type() == 'Individual':
            return record
        else:
            return None

    def get_family(self, xref):
        """ Return an object of class Family identified by xref """
        record = self.get_record(xref)
        if record.type() == 'Family':
            return record
        else:
            return None

    # Private methods

    def _parse(self,file):
        # open file
        # go through the lines
        f = open(file)
        number = 1
        for line in f.readlines():
            self._parse_line(number,line.decode("utf-8"))
            number += 1

        self._init()

    def _parse_line(self,number,line):
        # each line should have: Level SP (Xref SP)? Tag (SP Value)? (SP)? NL
        # parse the line
	try:
	  (l,p,t,v) = parse_line(line)
        except Exception as e:
	   print_exc(e)
	   self._error(number,"Syntax error in GEDCOM file")

        # create the line
        if l > self._current_level + 1:
            self._error(number,"Structure of GEDCOM file is corrupted")

        if l == 0: #current line is in fact a brand new record
            if t == "INDI":
                e = Individual(l,p,t,v,self.record_dict())
            elif t == "FAM":
                e = Family(l,p,t,v,self.record_dict())
            elif t == "OBJE":
                e = Multimedia(l,p,t,v,self.record_dict())
            elif t == "NOTE":
                e = Note(l,p,t,v,self.record_dict())
            elif t == "REPO":
                e = Repository(l,p,t,v,self.record_dict())
            elif t == "SOUR":
                e = Source(l,p,t,v,self.record_dict())
            elif t == "SUBN":
                e = Submission(l,p,t,v,self.record_dict())
            elif t == "SUBM":
                e = Submitter(l,p,t,v,self.record_dict())
            else:
                e = Record(l,p,t,v,self.record_dict())
        else:
            e = Line(l,p,t,v,self.record_dict())

        if p != '':
            self._record_dict[p] = e

        if l > self._current_level:
            self._current_line.add_child(e)
            e.add_parent_line(self._current_line)
        else:
            # l.value <= self._current_level:
            while (self._current_line.level() != l - 1):
                self._current_line = self._current_line.parent_line()
            self._current_line.add_child(e)
            e.add_parent_line(self._current_line)

        # finish up
        self._current_level = l
        self._current_line = e

    def _error(self,number,text):
        error = "Gedcom format error on line " + unicode(number) + ': ' + text
        raise GedcomParseError(error)

    def _print(self,file=None):
       if file != None:
          f = codecs.open( file, "w", "UTF-8" )
          for e in self.line_list(): f.write( unicode(e) + "\n" )
          f.close()
       else:
          for e in self.line_list(): print unicode(e)

