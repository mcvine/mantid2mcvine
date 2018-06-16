#!/usr/bin/env python

import unittest
import os

class Test(unittest.TestCase):

    def test_create_template(self):
        here = os.path.dirname(__file__)
        from mantid2mcvine.instrument_xml.Bootstrap_mantid_idf import InstrumentFactory as IF, units
        factory = IF()
        from instrument.geometry import shapes
        detsys_shape = shapes.hollowCylinder(in_radius=2., out_radius=3., height=3.)
        class tube_info:
            pressure = 10.*units.pressure.atm
            radius = .5 * units.length.inch
            gap = 0.08 * units.length.inch
        out = os.path.join(here, 'mcvine.xml')
        factory.construct(
            name='mantid', idfpath=os.path.join(here, "instrument_xml/xxxxMCVINETESTxxxx_Definition.xml"),
            ds_shape = detsys_shape, tube_info=tube_info,
            xmloutput=out,
        )
        this = load(out)
        expected = load(os.path.join(here, 'expected/mcvine.xml'))
        self.assert_(elements_equal(this, expected))
        return


def load(path):
    import xml.etree.ElementTree as ET
    tree = ET.parse(path)
    root = tree.getroot()
    return root

def elements_equal(e1, e2):
    if e1.tag != e2.tag:
        print "tag: %r != %r" % (e1.tag, e2.tag)
        return False
    _strip = lambda v: (v or '').strip() # deal with None
    if _strip(e1.text) != _strip(e2.text):
        print "text: %r != %r" % (e1.text, e2.text)
        return False
    if _strip(e1.tail) != _strip(e2.tail):
        print "tail: %r != %r" % (e1.tail, e2.tail)
        return False
    if e1.attrib != e2.attrib:
        print "attrib: %r != %r" % (e1.attrib, e2.attrib)
        return False
    if len(e1) != len(e2):
        print "len: %r != %r" % (len(e1), len(e2))
        return False
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

if __name__ =='__main__': unittest.main()

