from ast import literal_eval

from collections import OrderedDict
from itertools import permutations, product

from multiset import Multiset

import xml.etree.ElementTree as ET

from CPNParser.CPNModel import CPNModel
from CPNParser.helpers import next_key, prev_key, generate_permutations

model = CPNModel('../../data/DotAndBoxes/COLORED/DotAndBoxes2.pnml')

print(model.types['playercount'].pnml_type)

arc = model.arcs['arc46']

print(arc.arc_expression.variables)

print(Multiset('aaab').items())

od = OrderedDict([('a', 'aa'), ('b', 'bb'), ('c', 'cc')])

print(next_key(od, 'b'))
print(prev_key(od, 'b'))

print(model.types['Position'].constants)

print(model.find_color_type('Position1').type)

print(list(('a', 'b', 'c')))

expression = model.transitions['Lose2'].guard_expression
variables = expression.variables
print(variables)

variable_types = [list(model.types[model.variables[item].type].constants.keys()) for item in variables]

print(variable_types)

bindings = model.transitions['Lose2'].bindings

for b in bindings:
    print(b)
    evaluation = expression.evaluate(model, b)
    print(evaluation)


print(model.places['IsWinner'].initial_marking.evaluate(model))


arc_expression = model.arcs['arc46'].arc_expression
arc_variables = arc_expression.variables
arc_variable_types = [list(model.types[model.variables[item].type].constants.keys()) for item in arc_variables]

arc_bindings = list(product(*arc_variable_types))

print(arc_variables)
for a in arc_bindings:
    print(a)
    print(arc_expression.evaluate(model, dict(zip(arc_variables, a))))


transition_id = '{0};{1}'.format('Lose2', model.transitions['Lose2'].bindings[0])
print()
print(literal_eval(transition_id.split(';')[1]))

# ptmodel = model.to_pt_net()

# print(ptmodel.transitions)
# print(ET.tostring(ptmodel.to_pnml().getroot(), short_empty_elements=False))

# ptmodel.to_pnml().write('../../data/DotAndBoxes/TEST/DotAndBoxes2.pnml', short_empty_elements=False)

trouble_model = CPNModel("../../data/mcc2016-models/CSRepetitions-COL-02/model.pnml")

trouble_pt = trouble_model.to_pt_net()

print(ET.tostring(trouble_pt.to_pnml().getroot(), short_empty_elements=False))
