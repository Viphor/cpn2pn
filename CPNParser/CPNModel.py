import xml.etree.ElementTree as ET
from ast import literal_eval
from multiprocessing.pool import Pool

from collections import OrderedDict, ChainMap
from itertools import product, chain

from functools import partial

from CPNParser import constants
from CPNParser.expressions import Expression
from .helpers import get_tag, get_namespace
import CPNParser.PTModel as pt

__MULTI_THREADED = False


def to_pt_net(obj, arg=None):
    if arg:
        return obj.to_pt_net(arg)
    return obj.to_pt_net()


def calculate_binding(binding, variables=None, transition=None):
    binding_dict = dict(zip(variables, binding))
    if not transition.guard_expression or transition.guard_expression.evaluate(transition.model, binding_dict):
        # transition.bindings.append(binding_dict)
        return binding_dict
    return None


class ColorType:
    def __init__(self, element: ET.Element, model):
        self.id = element.attrib['id']
        self.name = element.attrib['name']
        self.type = self.id

        item = element[0]
        self.pnml_type = get_tag(item)

        {
            'finiteenumeration': self.__finite_enumeration,
            'cyclicenumeration': self.__finite_enumeration,
            'dot': self.__dot,
            'productsort': self.__product_sort,
        }[self.pnml_type](item, model)

        self.size = len(self.constants)

    def __finite_enumeration(self, element: ET.Element, model):
        self.constants = OrderedDict([(const.attrib['id'], const.attrib['name']) for const in element])

    def __dot(self, element, model):  # the element parameter is for consistency.
        self.constants = OrderedDict({'dotconstant': 'dot'})

    def __product_sort(self, element, model):
        self.components = [t.attrib['declaration'] if get_tag(t) == 'usersort' else 'dot' for t in element]
        self.constants = list(product(*[model.types[t].constants for t in self.components]))


class Variable:
    def __init__(self, element: ET.Element):
        self.id = element.attrib['id']
        self.name = element.attrib['name']
        self.type = element[0].attrib['declaration']


class Place:

    def __init__(self, element: ET.Element, model):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.name = element.find('./{0}name/{0}text'.format(ns)).text
        self.type = element.find('./{0}type/{0}structure/*'.format(ns)).attrib['declaration']
        self.model = model

        initial_marking = element.find('./{0}hlinitialMarking/{0}structure'.format(ns))
        if initial_marking:
            self.__set_initial_marking(initial_marking)
        else:
            self.initial_marking = None

    def __set_initial_marking(self, element):
        self.initial_marking = Expression(element[0], 'initial_marking')

    def to_pt_net(self) -> dict:
        colors = self.model.types[self.type].constants
        return {'{0};{1}'.format(self.id, color): pt.Place(
            '{0};{1}'.format(self.id, color),
            '({0};{1})'.format(self.name, color),
            self.initial_marking.evaluate(self.model).get(color, 0) if self.initial_marking else 0
        ) for color in colors}


class Transition:

    def __init__(self, element: ET.Element, model):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.name = element.find('./{0}name/{0}text'.format(ns)).text
        self.model = model

        guard = element.find('./{0}condition/{0}structure'.format(ns))

        if guard:
            self.__set_guard_expression(guard)
        else:
            self.guard_expression = None
        self.bindings = []
        self.calculate_bindings()

    def __set_guard_expression(self, element):
        self.guard_expression = Expression(element[0], 'guard_expression')

    def calculate_bindings(self):
        variable_types = []
        variables = []

        if self.guard_expression:
            variables += self.guard_expression.variables

        connected_arcs = [arc for arc in self.model.arcs.values() if arc.source == self.id or arc.target == self.id]
        variables += list(chain.from_iterable([arc.arc_expression.variables for arc in connected_arcs]))

        variables = list(set(variables))
        variable_types += [
            list(self.model.types[self.model.variables[item].type].constants.keys())
            for item in variables
        ]

        if constants.USE_MULTIPLE_THREADS:  # TODO:1
            with Pool(constants.NO_THREADS) as p:
                self.bindings = [binding
                                 for binding in
                                 p.map(partial(
                                     calculate_binding,
                                     variables=variables,
                                     transition=self
                                 ), product(*variable_types)) if binding]
        else:
            for binding in product(*variable_types):
                binding_dict = dict(zip(variables, binding))
                if not self.guard_expression or self.guard_expression.evaluate(self.model, binding_dict):
                    self.bindings.append(binding_dict)

    def to_pt_net(self) -> dict:
        bindings = self.bindings
        if not bindings:
            return {self.id: pt.Transition(self.id, self.name)}
        return {'{0};{1}'.format(self.id, binding): pt.Transition(
            '{0};{1}'.format(self.id, binding),
            '({0};{1})'.format(self.name, binding)
        ) for binding in bindings}


class Arc:
    def __init__(self, element: ET.Element, model):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.source = element.attrib['source']
        self.target = element.attrib['target']
        self.model = model

        inscription = element.find('./{0}hlinscription/{0}structure'.format(ns))
        if inscription:
            self.__set_arc_expression(inscription)

    def __set_arc_expression(self, element):
        self.arc_expression = Expression(element[0], 'arc_expression')

    def get_place(self):
        try:
            list(self.model.places.keys()).index(self.source)
            return self.source, 'source'
        except ValueError:
            pass
        list(self.model.places.keys()).index(self.target)
        return self.target, 'target'

    def get_transition(self):
        try:
            list(self.model.transitions.keys()).index(self.source)
            return self.source, 'source'
        except ValueError:
            pass
        list(self.model.transitions.keys()).index(self.target)
        return self.target, 'target'

    def to_pt_net(self, transitions) -> dict:
        res = {}
        trans, _ = self.get_transition()
        for transition in transitions[trans].keys():
            place, direction = self.get_place()
            transition_parts = transition.split(';', 1)
            if len(transition_parts) < 2:
                transition_parts = list(transition_parts) + ['{}']
            colors = self.arc_expression.evaluate(self.model, literal_eval(transition_parts[1]))
            for color in colors.distinct_elements():
                arc_id = '{0};{1};{2}'.format(self.id, color, transition_parts[1])
                place_id = '{0};{1}'.format(place, color)

                arc = pt.Arc(
                        arc_id,
                        place_id if direction == 'source' else transition,
                        place_id if direction == 'target' else transition,
                        colors.get(color, 0)
                )
                if arc.weight > 0:
                    res.update({arc_id: arc})
        return res


# Parser based upon http://www.pnml.org/version-2009/version-2009.php
class CPNModel:

    def __init__(self, xml: str, net_id: str = None):
        tree = ET.parse(xml)
        root = tree.getroot()
        self.__ns = get_namespace(root)
        self.xml_net = root[0]
        if net_id:
            self.xml_net = root.find("./[@id='{}']".format(net_id))
        self.name = self.xml_net.attrib['id']

        self.__parse_types()
        self.__parse_net('place', Place)
        self.__parse_net('arc', Arc)
        self.__parse_net('transition', Transition)

    def __parse_types(self):
        decls = self.xml_net.find('./{0}declaration/{0}structure/{0}declarations'.format(self.__ns))
        self.types = {}
        self.variables = {}

        for decl in decls:
            {
                'namedsort': lambda: self.types.update({decl.attrib['id']: ColorType(decl, self)}),
                'variabledecl': lambda: self.variables.update({decl.attrib['id']: Variable(decl)}),
            }[get_tag(decl)]()

        color_count = sum([color.size for color in self.types.values()])
        constants.USE_MULTIPLE_THREADS = color_count > constants.SINGLE_THREAD_COLOR_LIMIT

    def __parse_net(self, part, clazz):
        parts = self.xml_net.findall('./{0}page/{0}{1}'.format(self.__ns, part))

        setattr(self, part + 's', {})

        for p in parts:
            getattr(self, part + 's', {}).update({p.attrib['id']: clazz(p, self)})

    def find_color_type(self, color) -> ColorType:
        if isinstance(color, str):
            for _, color_type in self.types.items():
                if color_type.pnml_type != 'productsort' and color in color_type.constants.keys():
                    return color_type
        elif isinstance(color, list):
            color = [self.find_color_type(c).type for c in color]
            for _, color_type in self.types.items():
                if color_type.pnml_type == 'productsort' and color == color_type.components:
                    return color_type
        raise LookupError('Color is not in any ColorType!')

    def to_pt_net(self) -> pt.PTModel:
        if constants.USE_MULTIPLE_THREADS:  # TODO:1
            with Pool(constants.NO_THREADS) as p:
                places = dict(ChainMap(*p.map(to_pt_net, self.places.values())))
                pt_trans = p.map(to_pt_net, self.transitions.values())
                transitions = {next(iter(transition)).split(';')[0]: transition for transition in pt_trans}
                arcs = dict(ChainMap(*p.map(partial(to_pt_net, arg=transitions), self.arcs.values())))

                return pt.PTModel(
                    places,
                    dict(ChainMap(*list(transitions.values()))),
                    arcs,
                    self.name
                )
        else:
            places = dict(ChainMap(*[place.to_pt_net() for place in self.places.values()]))
            transitions = {transition.id: transition.to_pt_net() for transition in self.transitions.values()}
            arcs = dict(ChainMap(*[arc.to_pt_net(transitions) for arc in self.arcs.values()]))

            return pt.PTModel(
                places,
                dict(ChainMap(*list(transitions.values()))),
                arcs,
                self.name
            )
