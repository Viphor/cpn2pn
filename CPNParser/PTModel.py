import xml.etree.ElementTree as ET


class Place:
    def __init__(self, id, name, initial_marking=0):
        self.id = id
        self.name = name
        self.initial_marking = initial_marking

    def to_pnml(self):
        elem = ET.Element('place', {'id': self.id})
        name = ET.SubElement(elem, 'name')
        name_text = ET.SubElement(name, 'text')
        name_text.text = self.name
        if self.initial_marking:
            initial_marking = ET.SubElement(elem, 'initialMarking')
            initial_marking_text = ET.SubElement(initial_marking, 'text')
            initial_marking_text.text = str(self.initial_marking)
        return elem


class Transition:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def to_pnml(self):
        elem = ET.Element('transition', {'id': self.id})
        name = ET.SubElement(elem, 'name')
        name_text = ET.SubElement(name, 'text')
        name_text.text = self.name
        return elem


class Arc:
    def __init__(self, id, source, target, weight):
        self.id = id
        self.source = source
        self.target = target
        self.weight = weight

    def to_pnml(self):
        elem = ET.Element('arc', {
            'id': self.id,
            'source': self.source,
            'target': self.target
        })
        if self.weight > 1:
            inscription = ET.SubElement(elem, 'inscription')
            inscription_text = ET.SubElement(inscription, 'text')
            inscription_text.text = str(self.weight)
        return elem


class PTModel:
    def __init__(self, places, transitions, arcs, name=''):
        self.name = name
        self.places = places
        self.transitions = transitions
        self.arcs = arcs

    def to_pnml(self):
        pnml = ET.Element('pnml', {'xmlns': 'http://www.pnml.org/version-2009/grammar/pnml'})
        net = ET.SubElement(pnml, 'net', {
            'id': self.name,
            'type': 'http://www.pnml.org/version-2009/grammar/pnml'
        })
        page = ET.SubElement(net, 'page', {'id': 'page0'})

        for place in self.places.values():
            page.append(place.to_pnml())
        for transition in self.transitions.values():
            page.append(transition.to_pnml())
        for arc in self.arcs.values():
            page.append(arc.to_pnml())

        name = ET.SubElement(net, 'name')
        name_text = ET.SubElement(name, 'text')
        name_text.text = self.name

        et = ET.ElementTree(pnml)

        return et
