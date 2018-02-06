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
        factory.construct(
            name='mantid', idfpath=os.path.join(here, "instrument_xml/xxxxMCVINETESTxxxx_Definition.xml"),
            ds_shape = detsys_shape, tube_info=tube_info,
            xmloutput=os.path.join(here, 'mcvine.xml')
        )
        return

if __name__ =='__main__': unittest.main()

