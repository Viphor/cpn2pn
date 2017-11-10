def get_namespace(element):
    if element.tag[0] == '{':
        return element.tag[:element.tag.index('}') + 1]
    return ''


def get_tag(element):
    if element.tag[0] == '{':
        return element.tag.split('}')[1]
    return element.tag


def append_ns(dct, ns):
    if not ns:
        return dct
    return {ns + key: value for key, value in dct.items()}


class Sort:
    def __init__(self, element):
        self.type = get_tag(element)
        self.__ns = get_namespace(element)

        {
            'finiteenumeration': self.__finite_enumeration,
            'cyclicenumeration': self.__finite_enumeration,
            'dot': self.__dot,
        }[self.type](element)

    def __finite_enumeration(self, element):
        self.constants = {const.attrib['id']: const.attrib['name'] for const in element}

    def __dot(self, element):  # the element parameter is for consistency.
        self.constants = {'dotconstant': 'dot'}


class Declaration:

    def __init__(self, element, types=None):
        self.id = element.attrib['id']
        self.name = element.attrib['name']
        self.type = get_tag(element)
        if not types:
            self.sort = Sort(element[0])
        else:
            self.sort = element[0].attrib['declaration']


class Place:

    def __init__(self, element):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.name = element.find('./{0}name/{0}text'.format(ns)).text
        self.type = element.find('./{0}type/{0}structure/*'.format(ns)).attrib['declaration']

        initial_marking = element.find('./{0}hlinitialmarking/{0}structure'.format(ns))
        if initial_marking:
            self.__set_initial_marking(initial_marking)

    def __set_initial_marking(self, element):
        pass


class Transition:

    def __init__(self, element):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.name = element.find('./{0}name/{0}text'.format(ns)).text


class Arc:

    def __init__(self, element):
        ns = get_namespace(element)
        self.id = element.attrib['id']
        self.source = element.attrib['source']
        self.target = element.attrib['target']
