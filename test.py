import unittest
from CPNParser.model import CPNModel


class TestCPNModelMethods(unittest.TestCase):
    voters_const = {
        'Voters1': '1',
        'Voters2': '2',
        'Voters3': '3',
        'Voters4': '4',
        'Voters5': '5',
        'Voters6': '6',
        'Voters7': '7',
        'Voters8': '8',
        'Voters9': '9',
        'Voters10': '10',
    }

    def setUp(self):
        self.model = CPNModel('../../data/Referendum/COLORED/referendum-10.pnml')

    def test_name(self):
        self.assertEqual(self.model.name, 'Referendum-COL-0010', 'Either net not found, or wrong net found.')

    def test_cyclic_enum(self):
        self.assertEqual(self.model.types['Voters'].sort.constants, self.voters_const, 'Constants are not correct')

    def test_dot(self):
        self.assertEqual(self.model.types['dot'].sort.constants, {'dotconstant': 'dot'}, 'Dot constant is not correct')

    def test_variable_decl(self):
        self.assertEqual(self.model.types[self.model.types['varv'].sort].sort.constants, self.voters_const,
                         'No type declared matching varv')

    def test_places(self):
        places = ['ready', 'voted_no', 'voted_yes', 'voting']

        self.assertEqual(list(self.model.places.keys()), places, 'Not all places were read')

    def test_transitions(self):
        transitions = ['start', 'no', 'yes']

        self.assertEqual(list(self.model.transitions.keys()), transitions, 'Not all transitions were read')

    def test_arcs(self):
        arcs = ['arc10', 'arc11', 'arc12', 'arc13', 'arc14', 'arc15']

        self.assertEqual(list(self.model.arcs.keys()), arcs, 'Not all arcs were read')


if __name__ == '__main__':
    unittest.main()
