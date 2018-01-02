from collections import OrderedDict
from xml.etree.ElementTree import Element


def get_namespace(element: Element) -> str:
    if element.tag[0] == '{':
        return element.tag[:element.tag.index('}') + 1]
    return ''


def get_tag(element: Element) -> str:
    if element.tag[0] == '{':
        return element.tag.split('}')[1]
    return element.tag


def append_ns(dct: dict, ns: str) -> dict:
    if not ns:
        return dct
    return {ns + key: value for key, value in dct.items()}


def next_key(dct: OrderedDict, key):
    l = list(dct.keys())
    i = l.index(key)
    if i < len(l) - 1:
        return l[i + 1]
    else:
        return l[0]


def prev_key(dct: OrderedDict, key):
    l = list(dct.keys())
    i = l.index(key)
    if i > 0:
        return l[i - 1]
    else:
        return l[len(l) - 1]


def key_order(dct: OrderedDict, left, right) -> int:
    i = list(dct.keys()).index(left)
    j = list(dct.keys()).index(right)
    return i - j


def generate_permutations(*args):
    if len(args) > 1:
        permutations = generate_permutations(*args[1:])
        return [list(y).append(x) for x in list(args[0]) for y in permutations]
    elif len(args) == 1:
        return list(args[0])
    else:
        return []
