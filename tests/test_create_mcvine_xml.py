#!/usr/bin/env python

import unittest
import os

class Test(unittest.TestCase):

    def test_create_template(self):
        here = os.path.dirname(__file__)
        from mantid2mcvine.instrument_xml.Bootstrap_mantid_idf_SNS_DGS import InstrumentFactory as IF, units
        factory = IF()
        from instrument.geometry import shapes
        detsys_shape = shapes.hollowCylinder(in_radius=2., out_radius=3., height=3.)
        out = os.path.join(here, 'mcvine.xml')
        factory.construct(
            name='mantid', idfpath=os.path.join(here, "instrument_xml/xxxxMCVINETESTxxxx_Definition.xml"),
            ds_shape = detsys_shape,
            xmloutput=os.path.join(here, 'mcvine.xml')
        )
        expected = os.path.join(here, 'expected/mcvine.xml')
        from mantid2mcvine.testutils import xml_equal
        self.assertTrue(xml_equal(out, expected))
        return


if __name__ =='__main__': unittest.main()

