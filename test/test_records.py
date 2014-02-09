import unittest
import os
from simplepyged.gedcom import *


class McIntyreTest(unittest.TestCase):
    """Unit tests for records.py using mcintyre.ged."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/mcintyre.ged'))
        self.kim = self.g.get_individual('@P405313470@')
        self.marsha = self.g.get_individual('@P405342543@')
        self.mary = self.g.get_individual('@P405366386@')
        self.chris = self.g.get_individual('@P405749335@')
        self.barbara = self.g.get_individual('@P407946950@')


    def test_individual(self):
        """Testing class Individual"""
        self.assertEqual(self.mary.type(), 'Individual')
       
        self.assertEqual(self.mary.birth().dateplace(), ('19 Nov 1923', 'Louisiana, USA'))
        self.assertEqual(self.mary.alive(), True)
        self.assertEqual(self.mary.father().alive(), False)
        self.assertEqual(self.mary.father().death().dateplace(), ('19 Aug 1975', 'Bastrop, Louisiana'))
        self.assertEqual(self.mary.sex(), 'F')
        self.assertEqual(self.mary.given_name(), 'Mary Christine')
        self.assertEqual(self.mary.surname(), 'Hern')
        self.assertEqual(self.mary.fathers_name(), 'Thomas Clyde')

        self.assertEqual(self.mary.deceased(), False)
        self.assertEqual(self.mary.death(), None)
           
        self.assertEqual(self.mary.parent_family().xref(), '@F5@')
        self.assertEqual(self.mary.parent_family().husband().xref(), '@P405368888@')
        self.assertEqual(map(lambda x: x.xref(), self.mary.parent_families()), ['@F5@'])
        self.assertEqual(map(lambda x: x.husband().xref(), self.mary.parent_families()), ['@P405368888@'])
        self.assertEqual(self.mary.father().xref(), '@P405368888@')
        self.assertEqual(self.mary.mother().xref(), '@P405538002@')
        self.assertEqual(self.mary.family().xref(), '@F4@')
        self.assertEqual(map(lambda x: x.xref(), self.mary.families()), ['@F4@'])
        self.assertEqual(self.mary.father().children(), [self.mary])

    def test_family(self):
        """Testing class Family"""
        fam = self.g.get_family('@F8@')

        self.assertEqual(fam.marriage().dateplace(), ('22 Oct 1821', 'Jefferson County, Mississippi, USA'))

        daniel = fam.children()[0]
        calvin = fam.children()[2]

        self.assertEqual(map(lambda x: x.xref(), daniel.siblings()), ['@P405608614@', '@P405613353@', '@P405421877@'])
        self.assertEqual(daniel.mutual_parent_families(calvin), [fam])
        
        self.assertEqual(map(lambda x: x.xref(), self.kim.common_ancestor_families(self.barbara)), ['@F4@'])
        
        michael = self.kim.siblings()[1]
        self.assertEqual(self.kim.mutual_parent_families(michael), self.kim.parent_families())
        self.assertEqual(self.kim.mutual_parent_families(self.barbara), [])

    def test_ancestors(self):
        """Testing Individual methods concerned with finding ancestors"""
        self.assertRaises(MultipleReturnValues, self.mary.common_ancestor, self.mary)
        self.assertEqual(self.mary.common_ancestors(self.mary), [self.mary.father(), self.mary.mother()])
        self.assertEqual(self.mary.common_ancestors(self.mary.father()), [self.mary.father().father(), self.mary.father().mother()])
        self.assertRaises(MultipleReturnValues, self.mary.father().common_ancestor, self.mary)
        self.assertEqual(self.mary.father().common_ancestors(self.mary), self.mary.father().parents())
        
        self.assertEqual(self.mary.common_ancestor_families(self.mary), self.mary.parent_families())
        self.assertEqual(self.mary.common_ancestor_families(self.mary.father()), self.mary.father().parent_families())
        self.assertEqual(self.mary.father().common_ancestor_families(self.mary), self.mary.father().parent_families())

        self.marys_husband = self.g.get_individual('@P405364205@')
        self.assertRaises(MultipleReturnValues, self.barbara.common_ancestor, self.chris)
        self.assertEqual(self.chris.common_ancestors(self.barbara), [self.marys_husband, self.mary])
        self.assertEqual(self.chris.common_ancestors(self.barbara), [self.marys_husband, self.mary])
        self.assertEqual(self.chris.common_ancestor_families(self.barbara), self.mary.families())
        self.assertEqual(self.barbara.common_ancestor_families(self.chris), self.mary.families())


    def test_relatives(self):
        """Testing Individual methods concerned with finding a relative"""
        self.assertEqual(self.barbara.is_relative(self.chris), True)
        self.assertEqual(self.chris.is_relative(self.barbara), True)

        self.assertEqual(self.barbara.distance_to_ancestor(self.mary), 1)
        self.assertEqual(self.chris.distance_to_ancestor(self.mary), 3)
        
        self.assertTrue(self.marsha.is_relative(self.kim))
        self.assertTrue(self.kim.is_relative(self.marsha))

        self.assertFalse(self.marsha.is_parent(self.kim))
        self.assertTrue(self.kim.is_parent(self.marsha))

        self.assertFalse(self.marsha.is_sibling(self.kim))
        self.assertFalse(self.kim.is_sibling(self.marsha))

        self.assertFalse(self.marsha.is_parent(self.barbara))
        self.assertFalse(self.barbara.is_parent(self.marsha))

        self.assertTrue(self.marsha.is_sibling(self.barbara))
        self.assertTrue(self.barbara.is_sibling(self.marsha))

    def test_direct_ascendants(self):
        """Test relatives which are direct ascendants."""

        will = self.chris.father()
        self.assertEqual(self.barbara.is_relative(will), False)
        self.assertEqual(self.chris.is_parent(will), True)
        self.assertEqual(self.chris.is_relative(will), True)

        
    def test_down_paths(self):
        """Testing Individual.down_path(). """
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.mary)), ['@P405366386@'])
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.barbara)), ['@P405366386@', '@P407946950@'])
        self.assertEqual(Individual.down_path(self.mary, self.chris, 2), None)
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.chris, 3)), ['@P405366386@', '@P405342543@', '@P405313470@', '@P405749335@'])
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.chris, 10)), ['@P405366386@', '@P405342543@', '@P405313470@', '@P405749335@'])
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.chris)), ['@P405366386@', '@P405342543@', '@P405313470@', '@P405749335@'])


    def test_paths(self):
        """Testing paths to relatives. """
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.chris.path_to_relative(self.barbara)), [('@P405749335@', 'start'), ('@P405313470@', 'parent'), ('@P405342543@', 'parent'), ('@P407946950@', 'sibling')])
        
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.barbara.path_to_relative(self.chris)), [('@P407946950@', 'start'), ('@P405342543@', 'sibling'), ('@P405313470@', 'child'), ('@P405749335@', 'child')])

    def test_spaces(self):
        """Testing indenting spaces"""
        ernest = self.g.get_individual('@P405362004@')

        self.assertEqual(ernest.type(), 'Individual')

        notes = ernest.children_tags('NOTE')
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].value(), '    Ma and Papa')
       
class WrightTest(unittest.TestCase):
    """Unit tests for records.py using wright.ged."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/wright.ged'))

    def test_individual(self):
        """Testing class Individual"""
        delores = self.g.get_individual('@I294@')

        self.assertEqual(delores.type(), 'Individual')

        self.assertEqual(delores.birth().dateplace(), ('24 JUL 1963', ''))
        self.assertEqual(delores.sex(), 'F')
        self.assertEqual(delores.given_name(), 'Delores')
        self.assertEqual(delores.surname(), 'Hyatt')
        self.assertEqual(delores.fathers_name(), 'HORACE')

        self.assertEqual(delores.deceased(), False)
        self.assertEqual(delores.death(), None)
        
        self.assertEqual(delores.parent_family().xref(), '@F159@')
        self.assertEqual(map(lambda x: x.xref(), delores.parent_families()), ['@F159@'])
        self.assertEqual(map(lambda x: x.xref(), delores.families()), ['@F295@'])
        self.assertEqual(delores in delores.father().children(), True)

    def test_family(self):
        """Testing class Family"""
        family = self.g.get_family('@F1@')

        self.assertEqual(family.husband().name(), ('Cosmond G', 'Wright'))
        self.assertEqual(family.married(), True)
        self.assertEqual(family.marriage().dateplace(), ('1 SEP 1973', 'Troronto, Ontario, Canada')) #sic :-)
        

if __name__ == '__main__':
    unittest.main()
