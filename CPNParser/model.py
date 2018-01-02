import xml.etree.ElementTree as ET
from collections import OrderedDict
from itertools import product

from CPNParser.expressions import Expression
from .helpers import get_tag, get_namespace


class ColorType:
    def __init__(self, element: ET.Element):
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
        }[self.pnml_type](item)

    def __finite_enumeration(self, element: ET.Element):
        self.constants = OrderedDict([(const.attrib['id'], const.attrib['name']) for const in element])

    def __dot(self, element):  # the element parameter is for consistency.
        self.constants = OrderedDict({'dotconstant': 'dot'})

    def __product_sort(self, element):
        self.components = [t.attrib['declaration'] if get_tag(t) == 'usersort' else 'dot' for t in element]


class Variable:
    def __init__(self, element: ET.Element):
        self.id = element.attrib['id']
        self.name = element.attrib['name']
        self.type = element[0].attrib['declaration']


class Place:

    def __init__(self, element: ET.Element):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.name = element.find('./{0}name/{0}text'.format(ns)).text
        self.type = element.find('./{0}type/{0}structure/*'.format(ns)).attrib['declaration']

        initial_marking = element.find('./{0}hlinitialMarking/{0}structure'.format(ns))
        if initial_marking:
            self.__set_initial_marking(initial_marking)

    def __set_initial_marking(self, element):
        self.initial_marking = Expression(element[0], 'initial_marking')


class Transition:

    def __init__(self, element: ET.Element):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.name = element.find('./{0}name/{0}text'.format(ns)).text

        guard = element.find('./{0}condition/{0}structure'.format(ns))
        if guard:
            self.__set_guard_expression(guard)

    def __set_guard_expression(self, element):
        self.guard_expression = Expression(element[0], 'guard_expression')
        self.bindings = []

    def calculate_bindings(self, model):
        variable_types = [
            list(model.types[model.variables[item].type].constants.keys()) for item in self.guard_expression.variables
        ]

        for binding in product(*variable_types):
            binding_dict = dict(zip(self.guard_expression.variables, binding))
            if self.guard_expression.evaluate(model, binding_dict):
                self.bindings.append(binding_dict)


class Arc:
    def __init__(self, element: ET.Element):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.source = element.attrib['source']
        self.target = element.attrib['target']

        inscription = element.find('./{0}hlinscription/{0}structure'.format(ns))
        if inscription:
            self.__set_arc_expression(inscription)

    def __set_arc_expression(self, element):
        self.arc_expression = Expression(element[0], 'arc_expression')


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
        self.__parse_net('transition', Transition)
        self.__parse_net('arc', Arc)

    def __parse_types(self):
        decls = self.xml_net.find('./{0}declaration/{0}structure/{0}declarations'.format(self.__ns))
        self.types = {}
        self.variables = {}

        for decl in decls:
            {
                'namedsort': lambda: self.types.update({decl.attrib['id']: ColorType(decl)}),
                'variabledecl': lambda: self.variables.update({decl.attrib['id']: Variable(decl)}),
            }[get_tag(decl)]()

    def __parse_net(self, part, clazz):
        parts = self.xml_net.findall('./{0}page/{0}{1}'.format(self.__ns, part))

        setattr(self, part + 's', {})

        for p in parts:
            getattr(self, part + 's', {}).update({p.attrib['id']: clazz(p)})

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

