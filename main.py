from collections import OrderedDict
from itertools import permutations, product

from multiset import Multiset

from CPNParser.model import CPNModel
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

bindings = list(product(*variable_types))

for b in bindings:
    print(b)
    evaluation = expression.evaluate(model, dict(zip(variables, b)))
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
