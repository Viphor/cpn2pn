import xml.etree.ElementTree as ET
from .helpers import get_tag, get_namespace, Declaration, Place, Transition, Arc


# Parser based upon http://www.pnml.org/version-2009/version-2009.php
class CPNModel:

    def __init__(self, xml, net_id=None):
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

        for decl in decls:
            {
                'namedsort': lambda: self.types.update({decl.attrib['id']: Declaration(decl)}),
                'variabledecl': lambda: self.types.update({decl.attrib['id']: Declaration(decl, self.types)}),
            }[get_tag(decl)]()

    def __parse_net(self, part, clazz):
        parts = self.xml_net.findall('./{0}page/{0}{1}'.format(self.__ns, part))

        setattr(self, part + 's', {})

        for p in parts:
            getattr(self, part + 's', {}).update({p.attrib['id']: clazz(p)})

    # def __parse_places(self):
    #     places = self.xml_net.findall('./{0}page/{0}place'.format(self.__ns))
    #
    #     self.places = {}
    #
    #     for place in places:
    #         self.places.update({place.attrib['id']: Place(place)})
    #
    # def __parse_transitions(self):
    #     transitions = self.xml_net.findall('./{0}page/{0}transistion'.format(self.__ns))
    #
    #     self.transitions = {}
    #
    #     for transition in transitions:
    #         self.transitions.update({transition.attrib['id']: Transition(transition)})
