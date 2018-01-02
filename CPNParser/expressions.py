from itertools import product
from xml.etree.ElementTree import Element

from multiset import Multiset

from CPNParser.helpers import get_namespace, next_key, prev_key, key_order, get_tag


def get_constituents(element: Element, typing, *args, **kwargs):
    left = eval_term(element[0], *args, **kwargs)
    if not isinstance(left, typing):
        raise Exception('Left constituent is not of type {0}!'.format(typing))
    right = eval_term(element[1], *args, **kwargs)
    if not isinstance(right, typing):
        raise Exception('Right constituent is not of type {0}!'.format(typing))
    return left, right


def ensure_color_types(model, left: str, right: str):
    left_color_type = model.find_color_type(left)
    right_color_type = model.find_color_type(right)

    if left_color_type.id != right_color_type.id:
        raise Exception('Colors are not of the same type!')

    return left_color_type


def __eval_dot_constant(element: Element, *args, **kwargs) -> str:
    if get_tag(element) != 'dotconstant':
        raise Exception('Element is not a variable!')
    return 'dotconstant'


def __eval_variable(element: Element, binding, *args, **kwargs) -> str:
    if get_tag(element) != 'variable':
        raise Exception('Element is not a variable!')
    val = binding[element.attrib['refvariable']]
    if not val:
        raise Exception('Variable is not bound!')
    return val


def __eval_user_operator(element: Element, *args, **kwargs) -> str:
    if get_tag(element) != 'useroperator':
        raise Exception('Element is not a user operator!')
    return str(element.attrib['declaration'])


def __eval_user_sort(element: Element, *args, **kwargs) -> str:
    if get_tag(element) != 'usersort':
        raise Exception('Element is not a user sort!')
    return str(element.attrib['declaration'])


def __eval_number_constant(element: Element, *args, **kwargs) -> int:
    if get_tag(element) != 'numberconstant':
        raise Exception('Element is not a number constant!')
    return int(element.attrib['value'])


def __eval_successor(element: Element, model, *args, **kwargs) -> str:
    if get_tag(element) != 'successor':
        raise Exception('Element is not a successor!')
    if not model:
        raise Exception('No model has been specified!')

    color = eval_term(element[0], model=model, *args, **kwargs)
    color_type = model.find_color_type(color)
    if color_type.pnml_type != 'cyclicenumeration':
        raise Exception('Only finite enumerations has successors')

    return next_key(color_type.constants, color)


def __eval_predecessor(element: Element, model, *args, **kwargs) -> str:
    if get_tag(element) != 'predecessor':
        raise Exception('Element is not a predecessor!')
    if not model:
        raise Exception('No model has been specified!')

    color = eval_term(element[0], model=model, *args, **kwargs)
    color_type = model.find_color_type(color)
    if color_type.pnml_type != 'cyclicenumeration':
        raise Exception('Only finite enumerations has predecessors')

    return prev_key(color_type.constants, color)


def __eval_tuple(element: Element, *args, **kwargs):
    if get_tag(element) != 'tuple':
        raise Expression('Element is not a tuple operator!')
    t = []
    for e in element:
        val = eval_term(e, *args, **kwargs)
        if not isinstance(val, (list, str)):
            raise Exception('Tuple element is not a color!')
        t.append(val)
    return tuple(t)


def __eval_number_of(element: Element, *args, **kwargs) -> Multiset:
    if get_tag(element) != 'numberof':
        raise Exception('Element is not a number of operator!')
    num = eval_term(element[0], *args, **kwargs)
    if not isinstance(num, int):
        raise Exception('The first child of the number of operator must evaluate to an integer!')
    color = eval_term(element[1], *args, **kwargs)
    if not isinstance(color, (str, list, tuple)):
        raise Exception('The second child of the number of operator must evaluate to a color')

    if isinstance(color, str):
        return Multiset({color: num})

    if isinstance(color, tuple):
        for c in list(color):
            if isinstance(c, list):
                ms = Multiset()
                for p in product(*color):
                    ms.add(p, num)
                return ms
        return Multiset({color: num})

    ms = Multiset()
    for col in color:
        ms.add(col, num)

    return ms


def __eval_all(element: Element, *args, **kwargs) -> list:
    if get_tag(element) != 'all':
        raise Exception('Element is not an all operator!')
    model = kwargs['model']
    color_type = model.types[eval_term(element[0], model=model, *args, **kwargs)]
    if not color_type:
        raise LookupError('Color type not found!')

    return [color for color in color_type.constants.keys()]


def __eval_add(element: Element, *args, **kwargs) -> Multiset:
    if get_tag(element) != 'add':
        raise Exception('Element is not an add operator!')
    ms = Multiset()
    for subterm in element:
        constituent = eval_term(subterm, *args, **kwargs)
        if not isinstance(constituent, Multiset):
            raise Exception('Constituent of add must be a multiset!')
        ms.update(constituent)

    return ms


def __eval_subtract(element: Element, *args, **kwargs) -> Multiset:
    if get_tag(element) != 'subtract':
        raise Exception('Element is not a subtract operator!')
    left = eval_term(element[0], *args, **kwargs)
    if not isinstance(left, Multiset):
        raise Exception('Left constituent of subtract must be a multiset!')
    right = eval_term(element[1], *args, **kwargs)
    if not isinstance(right, Multiset):
        raise Exception('Right constituent of subtract must be a multiset!')

    return left.difference(right)


def __eval_scalar_product(element: Element, *args, **kwargs) -> Multiset:
    if get_tag(element) != 'scalarproduct':
        raise Exception('Element is not a scalar product operator!')
    scalar = eval_term(element[0], *args, **kwargs)
    if not isinstance(scalar, int):
        raise Exception('Scalar of the scalar product is not an integer!')
    ms = eval_term(element[1], *args, **kwargs)
    if not isinstance(ms, Multiset):
        raise Exception('Multiset of the scalar product is not a multiset!')

    return ms.times(scalar)


def __eval_less_than(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) not in ['lt', 'lessthan']:
        raise Exception('Element is not a less than operator!')
    model = kwargs['model']
    left, right = get_constituents(element, str, *args, **kwargs)
    color_type = ensure_color_types(model, str(left), str(right))

    return key_order(color_type.constants, left, right) < 0


def __eval_greater_than(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) not in ['gt', 'greaterthan']:
        raise Exception('Element is not a greater than operator!')
    model = kwargs['model']
    left, right = get_constituents(element, str, *args, **kwargs)
    color_type = ensure_color_types(model, str(left), str(right))

    return key_order(color_type.constants, left, right) > 0


def __eval_less_than_eq(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) not in ['leq', 'lessthanorequal']:
        raise Exception('Element is not a less than or equal operator!')
    model = kwargs['model']
    left, right = get_constituents(element, str, *args, **kwargs)
    color_type = ensure_color_types(model, str(left), str(right))

    return key_order(color_type.constants, left, right) <= 0


def __eval_greater_than_eq(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) not in ['geq', 'greaterthanorequal']:
        raise Exception('Element is not a greater than or equal operator!')
    model = kwargs['model']
    left, right = get_constituents(element, str, *args, **kwargs)
    color_type = ensure_color_types(model, str(left), str(right))

    return key_order(color_type.constants, left, right) >= 0


def __eval_equality(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) not in ['eq', 'equality']:
        raise Exception('Element is not an equality operator!')
    model = kwargs['model']
    left, right = get_constituents(element, str, *args, **kwargs)
    color_type = ensure_color_types(model, str(left), str(right))

    return key_order(color_type.constants, left, right) == 0


def __eval_inequality(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) not in ['neq', 'inequality']:
        raise Exception('Element is not an inequality operator!')
    model = kwargs['model']
    left, right = get_constituents(element, str, *args, **kwargs)
    color_type = ensure_color_types(model, str(left), str(right))

    return key_order(color_type.constants, left, right) != 0


def __eval_not(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) != 'not':
        raise Exception('Element is not a not operator!')
    val = eval_term(element[0], *args, **kwargs)
    if not isinstance(val, bool):
        raise Exception('Cannot negate non boolean values!')

    return not val


def __eval_and(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) != 'and':
        raise Exception('Element is not an and operator!')
    left, right = get_constituents(element, bool, *args, **kwargs)

    return bool(left) and bool(right)


def __eval_or(element: Element, *args, **kwargs) -> bool:
    if get_tag(element) != 'or':
        raise Exception('Element is not an or operator!')
    left, right = get_constituents(element, bool, *args, **kwargs)

    return bool(left) or bool(right)


def eval_term(element: Element, *args, **kwargs):
    if get_tag(element) == 'subterm':
        return eval_term(element[0], *args, **kwargs)

    return {
        'dotconstant': __eval_dot_constant,
        'variable': __eval_variable,
        'useroperator': __eval_user_operator,
        'usersort': __eval_user_sort,
        'numberconstant': __eval_number_constant,
        'successor': __eval_successor,
        'predecessor': __eval_predecessor,
        'tuple': __eval_tuple,
        'numberof': __eval_number_of,
        'all': __eval_all,
        'add': __eval_add,
        'subtract': __eval_subtract,
        'scalarproduct': __eval_scalar_product,
        'lt': __eval_less_than,
        'lessthan':__eval_less_than,
        'gt': __eval_greater_than,
        'greaterthan': __eval_greater_than,
        'leq': __eval_less_than_eq,
        'lessthanorequal': __eval_less_than_eq,
        'geq': __eval_greater_than_eq,
        'greaterthanorequal': __eval_greater_than_eq,
        'eq': __eval_equality,
        'equality': __eval_equality,
        'neq': __eval_inequality,
        'inequality': __eval_inequality,
        'not': __eval_not,
        'and': __eval_and,
        'or': __eval_or,
    }[get_tag(element)](element, *args, **kwargs)


class Expression:
    def __init__(self, element: Element, sort):
        self.type = sort
        self.variables = []
        self.expression = element

        var = element.findall('.//{0}variable'.format(get_namespace(element)))
        for v in var:
            if v.attrib['refvariable'] not in self.variables:
                self.variables.append(v.attrib['refvariable'])

    def evaluate(self, model, binding: dict = {}):
        if set(self.variables) != set(binding.keys()):
            raise Exception('All variables must be bound in order to evaluate expression!')
        return eval_term(self.expression, binding=binding, model=model)
