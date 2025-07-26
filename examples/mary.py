#! /usr/bin/env python

"""
This is a simple example of printing a person with its closest
famiily on stdout.

The output is crude, so it is rather a poor example.
"""

from pyged.gedcom import *

g = Gedcom('mcintyre.ged')
mary = g.get_individual('@P405366386@')

print(mary.name())

#parents
print(mary.father().name())
print(mary.parent_family().husband().name())

#husband
print(map(lambda x: x.husband().name(), mary.families()))

#children
print(map(lambda x: x.name(), mary.children()))
