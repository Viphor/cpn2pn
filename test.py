import unittest

from multiset import Multiset

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

    @classmethod
    def setUpClass(cls):
        super(TestCPNModelMethods, cls).setUpClass()
        cls.model = CPNModel('../../data/Referendum/COLORED/referendum-10.pnml')
        cls.large_model = CPNModel('../../data/DotAndBoxes/COLORED/DotAndBoxes2.pnml')

    def setUp(self):
        self.model = TestCPNModelMethods.model
        self.large_model = TestCPNModelMethods.large_model

    def test_name(self):
        self.assertEqual(self.model.name, 'Referendum-COL-0010', 'Either net not found, or wrong net found.')

    def test_cyclic_enum(self):
        self.assertEqual(self.model.types['Voters'].constants, self.voters_const, 'Constants are not correct')

    def test_dot(self):
        self.assertEqual(self.model.types['dot'].constants, {'dotconstant': 'dot'}, 'Dot constant is not correct')

    def test_productsort(self):
        self.assertEqual(self.large_model.types['played'].components, ['Player', 'direction', 'Position', 'Position'])

    def test_find_color_type(self):
        self.assertEqual(self.model.find_color_type('Voters1').type, 'Voters')
        self.assertEqual(self.large_model.find_color_type(
            [
                'Player1',
                'Direction0',
                'Position0',
                'Position1'
            ]).type, 'played')

    def test_variable_decl(self):
        for _, v in self.model.variables.items():
            self.assertIn(v.type, self.model.types.keys())

    def test_places(self):
        places = ['ready', 'voted_no', 'voted_yes', 'voting']

        self.assertEqual(list(self.model.places.keys()), places, 'Not all places were read')

    def test_transitions(self):
        transitions = ['start', 'no', 'yes']

        self.assertEqual(list(self.model.transitions.keys()), transitions, 'Not all transitions were read')

    def test_arcs(self):
        arcs = ['arc10', 'arc11', 'arc12', 'arc13', 'arc14', 'arc15']

        self.assertEqual(list(self.model.arcs.keys()), arcs, 'Not all arcs were read')

    def test_expression_variables(self):
        test_arc = self.model.arcs['arc13']
        self.assertEqual(test_arc.arc_expression.variables, ['varv'])

        for _, arc in self.model.arcs.items():
            self.assertEqual(len(arc.arc_expression.variables), len(list(set(arc.arc_expression.variables))))

    def test_expression_evaluation(self):
        guard_expression = self.large_model.transitions['Lose2'].guard_expression
        self.assertEqual(guard_expression.evaluate(model=self.large_model, binding={
            'vard': 'Direction0',
            'varposH': 'Position0',
            'varposV': 'Position0',
            'vard1': 'Direction0',
            'varposH1': 'Position0',
            'varposV1': 'Position0'
        }), False)

        initial_marking = self.large_model.places['IsWinner'].initial_marking
        self.assertEqual(initial_marking.evaluate(
            self.large_model),
            Multiset({('Player1', 'Bool1'): 1,
                      ('Player2', 'Bool1'): 1})
        )

        arc_expression = self.large_model.arcs['arc46'].arc_expression
        self.assertEqual(arc_expression.evaluate(self.large_model, {
            'varposH': 'Position0',
            'varposV': 'Position0'
        }), Multiset({
            ('Direction0', 'Position1', 'Position0'): 1,
            ('Direction1', 'Position1', 'Position0'): 1,
            ('Direction1', 'Position1', 'Position1'): 1
        }))


if __name__ == '__main__':
    unittest.main()
