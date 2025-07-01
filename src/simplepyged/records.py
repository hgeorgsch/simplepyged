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

# Standard libraries
import string

__all__ = [ "Node", "Line", "Record", "Note", "Multimedia",
   "Repository", "Source", "Submitter", "Individual", "Family",
   "Associate" ]

# Other submodules
from .events import Event
from .errors import *

def parse_name(e):
    """
    Parse a gedcom NAME value to produce a pair (firstname, lastname).  
    Any suffix after the lastname will be ignored.
    """
    name = e.value().split('/')
    first = name[0].strip()
    if len(name) == 1: last = ""
    else: last = name[1].strip()
    return (first,last)

class Node(object):
    """
    A generic superclass for Gedcom Nodes, including files, records,
    lines, and other structures.  It handles parent and child nodes,
    as well as the level.  A file has a level of -1.
    """
    def __init__(self):
       self._children_lines = []
       self._parent_line = None
       self._level = -1

    def _init(self):
        """
        A method which GEDCOM parser runs after all lines are available.
        Subclasses should implement this method if they want to work with
        other Lines at parse time, but after all Lines are parsed. 
        """
        for e in self.children_lines(): e._init()
    def __iter__(self):
       return self._children_lines.__iter__()

    def line_list(self):
        """
        Return an iterator of all the lines in the Gedcom node.  The
        lines are in the same order as they appeared in the file.
        """
        for e in self.children_lines():
           yield e
           for c in e.line_list():
              yield c

    def level(self):
        """ Return the level of this node. """
        return self._level

    def children_lines(self):
        """ Return the child lines of this line """
        for i in self._children_lines: yield i

    def del_child_line(self,line):
        self._children_lines.remove(line)
    def add_child_line(self,line):
        """Add a child line to this line """
        self._children_lines.append(line)
        line.add_parent_line(self)
        
    def children_tags(self, tag):
        """
        Returns list of child lines whoses tag match the argument.
        """
        for c in self.children_lines():
            if c.tag() == tag: yield c
    def children_single_tag(self, tag):
        """
        Returns the first child node whose tag matches the argument.
        None is returned if no such child is found.
        """
        for c in self.children_lines():
            if c.tag() == tag: return c
        return None
    def children_single_val(self, tag):
       """
       None is returned if no such child is found.
       Returns the value of the first child node whose tag
       matches the argument.
       """
       R = self.children_single_tag(tag)
       if R != None: R = R.value()
       return R

    def parent_line(self):
        """ Return the parent node of this line """
        return self._parent_line

    def add_parent_line(self,line):
        """ Add a parent line to this line """
        self._parent_line = line
    def _xref_update(self,old,new):
       """Change every occurrnce of the old xref value to the
       new xref value."""
       if self._level > 0:
          v = self.value().strip()
          if v == old.strip(): 
             self._value = new
       if hasattr(self,"children_lines"):
          for n in self.children_lines():
              n._xref_update(old,new)

class Line(Node):
    """ Line of a GEDCOM file

    Each line in a Gedcom file has following format:

    level [xref] tag [value]

    where level and tag are required, and xref and value are optional.
    Lines are arranged hierarchically according to their level, and
    lines with a level of zero (called 'records') are at the top
    level.  Lines with a level greater than zero are children of their
    parent.

    A xref has the format @pname@, where pname is any sequence of
    characters and numbers.  The xref identifies the record being
    referenced to, so that any xref included as the value of any line
    points back to the original record.  For example, an line may have
    a FAMS tag whose value is @F1@, meaning that this line points to
    the family record in which the associated individual is a spouse.
    Likewise, an line with a tag of FAMC has a value that points to a
    family record in which the associated individual is a child.
    
    See a Gedcom file for examples of tags and their values.
    """

    def __init__(self,level,xref,tag,value,dict):
        """ Initialize a line.  You must include a level, xref,
        tag, value, and global line dictionary.  Normally initialized
        by the Gedcom parser, not by a user.
        """
        Node.__init__(self)
        # basic line info
        self._level = level
        self._xref = xref
        self._tag = tag
        self._value = value
        if not isinstance( dict, Node ): 
           print ( "dict:", type(dict), self )
        self._dict = dict

    def sources(self):
       """
       Return an iterator of all sources associated with the note.
       """
       return list( self.children_tags("SOUR") )

    def is_empty(self):
       """
       Return True if the Line has neither a (non-empty) value  nor
       a child node.  According to the Gedcom standard, such nodes
       should be ignored.
       """
       if self.value() != "": return False
       if len(self._children_lines) > 0: return False
       return True

    def type(self):
        """
        Return class name of this instance

        This can be used to determe if this line is Individual, Family,
        Note or some other record.  However, using the tag() method
        is a better approach if the data, rather than the class, is
        relevant.

        TODO: consider deprecating this.
        """
        return self.__class__.__name__

    def xref(self):
        """ Return the xref of this line """
        return self._xref
    def set_xref(self,ref):
        """ 
        Set the xref of this node.  
        If the xref is already set, an exception will be raised.
        """
        assert self._xref == None
        self._xref = ref
    
    def tag(self):
        """ Return the tag of this line """
        return self._tag

    def value_cont(self):
        """ 
        Return the value of this line, including any subsequent
        CONT/CONC lines.
        """
        v = self.value()
        for l in self.children_lines():
           if l.tag() == "CONT": v += "\n" + l.value()
           elif l.tag() == "CONC": v += l.value()
        return v
    def value(self):
        """ Return the value of this line """
        return self._value

    def children_single_record(self, tag):
        L = self.children_tag_records(tag)
        if len(L) == 0: return None
        else: return L[0]

    def children_tag_records(self, tag):
        """ 
        Returns list of records which are pointed by child lines
        with given tag.
        """
        lines = []
        for e in self.children_tags(tag):
            k = self._dict.get(e.value())
            if k != None:
               lines.append(self._dict.get(e.value()))
            else:
               print ( str(e) )
               print ( str(e.parent_line()) )
               raise GedcomMissingRecordError(
                     f"Undefined pointer: {e.value()}.  Missing record.") 
        return lines

    def gedcom(self):
        """ Return GEDCOM code for this line and all of its sub-lines """
        result = self
        for e in self.children_lines():
            result += '\n' + e.gedcom()
        return result

    def __str__(self):
        """ Format this line as its original string """
        result = str(self.level())
        if self.xref():
            result += ' ' + self.xref()
        result += ' ' + self.tag()
        if self.value():
            result += ' ' + self.value()
        return result

class Record(Line):
    """ Gedcom line with level 0 represents a record

    Child class of Line

    """
    
    def merge(self,other):
       """
       Merge the other Record with this one.
       """
       # 1.  Update all xref of other to point to self.
       self._dict._xref_update(other.xref(),self.xref())
       # 2.  Move all sub records of other into self.
       for n in other:
          self.add_child_line(n)
       # 3.  delete other
       self._dict.del_record(other)
       # Should do.
       # A.  Check for overlapping records, pruning duplicate info

    def _parse_generic_event_list(self, tag):
        """ Creates new event for each line with given tag"""
        retval = []
        for event_line in self.children_tags(tag):
           if not event_line.is_empty(): retval.append(Event(event_line))

        return retval
    def add_source(self,sour,page=None):
       level = self.level()+1
       src = Line( level=level, xref=None, tag="SOUR",
             value=sour, dict=self._dict )
       if page:
          src.add_child_line(
                Line( level=level+1, xref=None, tag="PAGE",
                   value=page, dict=self._dict ) )
       self.add_child_line( src )
       return src

class Note(Record): pass
class Multimedia(Record): pass
class Repository(Record): pass
class Source(Record): pass
class Submitter(Record): pass


class Individual(Record):
    """
    Gedcom record representing an individual.

    Child class of Record.
    """

    def __init__(self,level,xref,tag,value,dict):
        Record.__init__(self,level,xref,tag,value,dict)

    def _init(self):
        """ Implementing Line._init() """
        Record._init(self)

        # TODO: reconsider the need for these attributes
        self._parent_family = self.get_parent_family()
        self._families = self.get_families()

        self.birth_events = self._parse_generic_event_list("BIRT")
        self.death_events = self._parse_generic_event_list("DEAT")

    def sex(self):
        """
        Returns 'M' for males, 'F' for females, 'U' for unknown gender.
        """
        s = self.children_single_tag("SEX")
        if s == None: return "U"
        else: return s.value()

    def parent_family(self):
        return self._parent_family

    def families(self):
        return self._families

    def father(self):
       if self.parent_family() != None:
          if self.parent_family().husband() != None:
             return self.parent_family().husband()
       return None

    def mother(self):
       if self.parent_family() != None:
          if self.parent_family().wife() != None:
             return self.parent_family().wife()
       return None

    def children_count(self):
        retval = 0
        for f in self.families():
           retval += f.children_count()
        return retval

    def children(self):
        retval = []

        for f in self.families():
            for c in f.children():
                retval.append(c)

        return retval

    def get_families(self):
        """ Return a list of all of the family records of a person. """
        return self.children_tag_records("FAMS")

    def get_parent_family(self):
        """ Return a family record in which this individual is a child. """
        famc = self.children_tag_records("FAMC")
        
        if len(famc) > 1:
           print("Warning: multiple parent families not supported")
           print("Additional parents ignored for individual", self.xref())

        if len(famc) == 0:
            return None
        
        return famc[0]
    
    def name(self):
        """
        Return a person's names as a tuple: (first,last).

        The GIVN/SURN tags are used if provided, otherwise
        the name is parsed from the NAME value itself.
        """
        first = ""
        last = ""
        e = self.children_single_tag( "NAME" )
        if e.value() != "":
           (first,last) = parse_name(e)
        else:
           for c in e.children_lines():
              if c.tag() == "GIVN": first = c.value().strip()
              if c.tag() == "SURN": last = c.value().strip()
        return (first,last)

    def given_name(self):
        """ Return person's given name """
        try:
            return self.name()[0]
        except IndexError:
            return None

    def surname(self):
        """ Return person's surname """
        try:
            return self.name()[1]
        except IndexError:
            return None

    def fathers_name(self):
        """ Return father's name (patronymic) """
        return self.father().given_name()
        
    def birth(self):
        """
        Return the birth event of the individual.

        If the person has multiple birth events, then the returned
        event is the first one entered in the file.  This event
        should be treated as the `prefered' event according to
        Gedcom 5.5.1.

        For list of all birth events see self.birth_events().
        """

        if len(self.birth_events) == 0:
            return None

        return self.birth_events[0]

    def birth_year(self):
        """ Return the birth year of a person in integer format """

        if self.birth() == None: return None
        return self.birth().year()

    def alive(self):
        "Return True if individual lacks death entry."
        return self.death() is None

    def death(self):
        """
        Return the death event of the individual.

        If the person has multiple death events, then the returned
        event is the first one entered in the file.  This event
        should be treated as the `prefered' event according to
        Gedcom 5.5.1.

        For list of all death events see self.death_events().
        """

        if len(self.death_events) == 0:
            return None

        return self.death_events[0]

    def death_year(self):
        """ Return the death year of a person in integer format """

        if self.death() == None: return None
        return self.death().year() 

    def deceased(self):
        """ Check if a person is deceased """
        return not self.alive()

    def marriages(self):
        """ Return a list of marriage events for a person.
        """
        retval = []

        for f in self.families():
            for marr in f.marriage_events:
                retval.append(marr)

        return retval

    def marriage_years(self):
        """ Return a list of marriage years for a person, each in integer
        format.
        """
        def ret_year(marr):
            if marr.date is None:
                return ''
            return int(marr.year())

        return map(ret_year, self.marriages())

    def parents(self):
        """ Return list of parents of this Individual """

        if self.parent_family() is None:
            return []

        return self.parent_family().parents()
    
    def common_ancestor(self, relative):
        """ Find a common ancestor with a relative """

        if relative is None:
            return None

        me = {}
        him = {}
        
        me['new'] = [self]
        me['old'] = []
        him['new'] = [relative]
        him['old'] = []

        while(me['new'] != [] or him['new'] != []):
            #loop until we have no new ancestors to compare
            for p in me['new']: #compare new ancestors of both me and him
                if p in him['new']:
                    return p

            #compare new ancestors to old ones
            for p in me['new']:
                if p in him['old']:
                    return p

            for p in him['new']:
                if p in me['old']:
                    return p

            for l in [me, him]: # do this for both me and him
                new = []
                for p in l['new']: #find parents of all memebers of 'new'
                    new.extend(p.parents())
                new = filter(lambda x: x is not None, new)
                l['old'].extend(l['new']) #copy members of 'new' to 'old'
                l['new'] = new #parents of 'new' members became themselves 'new'

        return None

    def is_sibling(self, candidate):
        """ Determine if candidate is sibling of self """
        if self.parent_family() == candidate.parent_family():
            return True

        return False
        
    def is_relative(self, candidate):
        """ Determine if candidate is relative of self """
        if self.common_ancestor(candidate) is not None:
            return True

        return False
        
    def distance_to_ancestor(self, ancestor):
        """Distance to an ancestor given in number of generations

        Examples of return value:
        * from self to self: 0
        * from self to father: 1
        * from self to mother: 1
        * from self to grandfather: 2 """

        distance = 0
        ancestor_list = [self]

        while ancestor_list != []:
            if ancestor in ancestor_list:
                return distance

            new_list = []
            for a in ancestor_list:
                new_list.extend(a.parents())
                if None in new_list:
                    new_list.remove(None)

            ancestor_list = new_list

            distance += 1

        return None

    @staticmethod
    def down_path(ancestor, descendant, distance = None):
        """ Return path between ancestor and descendant (do not go deeper than distance depth) """

        if distance is not None:
            if distance <= 0:
                return None

        if ancestor.children() == []:
            return None
        
        if descendant in ancestor.children():
            return [ancestor]

        for c in ancestor.children():
            if distance is None:
                path = ancestor.down_path(c, descendant)
            else:
                path = ancestor.down_path(c, descendant, distance - 1)
            if path is not None:
                path.insert(0, ancestor)
                return path
    
        return None

    def path_to_relative(self, relative):
        """ Find path to a relative

        Returns a list of tuples (ancestor, direction) where:
        * ancestor is a person in the path between self and relative
        * direction is 'up' if this step in the path is parent of previous step
        * direction is 'down' if this step in the path is child of previous step
        """

        if relative == self:
            return []

        if relative in self.parents():
            return [[self, 'parent'], [relative, '']]
        
        common_ancestor = self.common_ancestor(relative)

        if common_ancestor is None: # is not relative
            return None

        if common_ancestor == self:
            my_path = []
        else:
            my_path = self.down_path(common_ancestor, self, self.distance_to_ancestor(common_ancestor))

        if common_ancestor == relative:
            his_path = []
        else:
            his_path = self.down_path(common_ancestor, relative, relative.distance_to_ancestor(common_ancestor))

        my_path.append(self)
        his_path.append(relative)

        my_path.reverse()

        full_path = []
        for step in my_path[:-1]: #my path without common ancestor
            full_path.append([step, 'parent'])

        # if two children of common ancestor are siblings, then leave
        # out common ancestor
        try:
            if full_path[-1][0].is_sibling(his_path[1]):
                full_path[-1][1] = 'sibling'
            else: # children of common ancestor are half-siblings, so
                  # we won't leave common ancestor out
                full_path.append([common_ancestor, 'child'])
        except IndexError: # sibling check didn't work out, we'll just
                           # put common ancestor in there
            full_path.append([common_ancestor, 'child'])
        
        for step in his_path[1:]: #his path without common ancestor
            full_path.append([step, 'child'])
        full_path[-1][1] = '' # last person doesn't have next person to relate to
            
        return full_path
        
    # Modifier methods
    def add_parents(self,f,m,force=False,marr=True):
       """
       Record the two individuals f and m as respectively
       father and mother of the individual.  If the individual
       previously is not a child of any family, then a new 
       family object is created.

       If there already is a family with this individual as
       a child, this family is amended.  Any parent (f or m)
       which is None will be ignored, thus not removing any
       previous parent.  If a new parent is given, and one
       already existed, the behaviour depends on the force
       argument; see Family.add_husband() and Family.add_wife()
       for details.
       """
       fam = self.parent_family()
       if fam == None:
          fam = Family( 0, None, "FAM", None, self._dict )
          if marr:
             fam.add_child_line( Line( 1, None, "MARR", "Y", self._dict ) )
          self._dict.add_record( fam )
       fam.add_child( self )
       if f != None: fam.add_husband( f, force )
       if m != None: fam.add_wife( m, force )
       return fam
    def add_family(self,f,spouse=None,marr=True):
       """
       Create a new family with the individual as a spouse.
       """
       fam = Family( 0, None, "FAM", None, self._dict )
       if marr:
          e = Line( 1, None, "MARR", "Y", self._dict )
          if type(marr) == str:
             e.add_child_line( Line( 2, None, "DATE", marr, self._dict ) )
          fam.add_child_line( e )
       self._dict.add_record( fam )
       # fam.add_child( self )
       return fam

class Family(Record):
    """ 
    Gedcom record representing a family.

    Child class of Record with additional methods to process
    family relations.
    """

    def __init__(self,level,xref,tag,value,dict):
        Record.__init__(self,level,xref,tag,value,dict)

    def _init(self):
        """
        Implementing Line._init()

        Initialise husband, wife and children attributes.
        """
        Record._init(self)
        
        # TODO: reconsider the usefulness of the following attributes
        self._husband = self.children_single_record("HUSB")
        self._wife = self.children_single_record("WIFE")
        self._children = self.children_tag_records("CHIL")
        self.marriage_events = self._parse_generic_event_list("MARR")


    def husband(self):
        """ Return the husband of this family """
        return self._husband

    def wife(self):
        """ Return the wife of this family """
        return self._wife

    def parents(self):
        """ Return list of parents in this family """
        return [self._husband, self._wife]

    def children_count_exact(self):
        """
        Return the number of children using the NCHI tag.
        """
        n = self.children_single_tag("NCHI")
        try:
           return int(n.value())
        except:
           return None

    def children_count(self):
        """
        Return the number of children.

        This uses the NCHI entry of Gedcom if present,
        otherwise it counts the children registered.
        """
        n = self.children_count_exact()
        if n != None: return n
        else: return len(self._children)

    def children(self):
        """ Return list of children in this family """
        return self._children

    def married(self):
        """ Return True if parents were married """
        return self.children_single_tag("MARR") != None

    def marriage(self):
        """ 
        Return the first marriage event from the record.

        If a family has only one marriage event (which is most common
        case), return that one marriage event. For list of all marriage
        events see self.marriage_events.
        """

        if len(self.marriage_events) == 0: return None
        return self.marriage_events[0]

    def is_relative(self, candidate):
        """ Determine if candidate is relative of a member of family """
        if self.husband() is not None and self.husband().is_relative(candidate):
            return True

        if self.wife() is not None and self.wife().is_relative(candidate):
            return True

        return False
        
    # Modifier methods
    def add_spouse(self,ind,force=False,tag=None):
       if self.xref() == None:
          raise ValueError( "Cannot add spouse to family without xref key." )
       if tag == None:
          sex = ind.sex()
          if sex == "F":
             tag = "WIFE"
          elif sex == "M":
             tag = "HUSB"
          else:
             print(ind.gedcom())
             raise ValueError( "Don't know whether spouse is husband or wife." )
       ref = ind.xref()
       t = self.children_single_tag( tag )
       if t != None:
          if force: raise NotImplementedError()
          else: raise Exception( f"The family already has a {tag} record." )
       self.add_child_line( Line( 1, None, tag, ref, dict=self._dict ) )
       ind.add_child_line( Line( 1, None, "FAMS", self.xref(), dict=self._dict ) )

    def add_husband(self,ind,force=False):
       return self.add_spouse(ind,force,"HUSB")

    def add_wife(self,ind,force=False):
       return self.add_spouse(ind,force,"WIFE")

    def add_child(self,ind,force=False):
       ref = ind.xref()
       self.add_child_line( Line( 1, None, "CHIL", ref, dict=self._dict ) )
       ind.add_child_line( Line( 1, None, "FAMC", self.xref(), dict=self._dict ) )

class Associate(Line):
    """
    Object to represent an ASSOCIATION_STRUCTURE in GEDCOM 5.5.1
    """

    def __init__(self,*a,**kw):
       Line.__init__(self,*a,**kw)
       self._type = None

    def _init(self):
       v = self.value()
       if valid_pointer(v):
          self._record = self._dict.get(v)
          if self._record == None: 
             raise GedcomMissingRecordError( "Missing record " + v )
       try: 
          self._type = self.children_single_tag("RELA").value()
       except: 
          self._type = None
       print ( "ASSO",v, self._type )
       Node._init(self)
    def get_type(self): return self._type
