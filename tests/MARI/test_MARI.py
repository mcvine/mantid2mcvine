#!/usr/bin/env python

import os
import mantid2mcvine as m2m
import instrument.geometry.operations

here = os.path.dirname(__file__)  or  '.'

instrument_name = 'MARI_virtual'
beamline =  997
mantid_idf = os.path.abspath(os.path.join(here, 'MARI_virtual_Definition.xml'))
mcvine_idf = os.path.abspath(os.path.join(here, 'MARI_mcvine.xml'))
template_nxs = os.path.abspath(os.path.join(here, 'MARI_template.nxs'))

cyl = m2m.shapes.hollowCylinder(in_radius=3.5, out_radius=4.5, height=1.6) # meters
detsys_shape = instrument.geometry.operations.rotate(cyl, angle=90., beam=1)
nbanks = 1
ntubesperpack = 8
npixelspertube = 128
nmonitors = 1
tofbinsize = 0.1 # mus

import unittest
import os

class Test(unittest.TestCase):

    def test_create_template(self):
        from mantid2mcvine.instrument_xml.Bootstrap_mantid_idf_MARI import InstrumentFactory as IF, units
        factory = IF()
        from instrument.geometry import shapes
        detsys_shape = shapes.hollowCylinder(in_radius=2., out_radius=3., height=3.)
        out = mcvine_idf
        factory.construct(
            name='mantid',
            idfpath=mantid_idf,
            ds_shape = detsys_shape,
            xmloutput=out,
            mantid_idf_row_typename_postfix = 'bank',
            mantid_idf_monitor_tag = 'monitor',
        )
        expected = os.path.join(here, 'expected/MARI_mcvine.xml')
        from mantid2mcvine.testutils import xml_equal
        self.assertTrue(xml_equal(out, expected))
        return

    def test(self):
        from mantid2mcvine.instrument_xml import Bootstrap_mantid_idf_MARI
        im = m2m.InstrumentModel(
            instrument_name, beamline, mantid_idf, mcvine_idf, template_nxs,
            detsys_shape,
            nmonitors = nmonitors,
            tofbinsize = tofbinsize,
            mantid_idf_row_typename_postfix = 'bank',
            mantid_idf_monitor_tag = 'monitor',
            instrument_factory = Bootstrap_mantid_idf_MARI.InstrumentFactory
        )
        im.convert()
        # im.mantid_install() # install mantid IDF to ~/.mantid
        return


if __name__ =='__main__': unittest.main()
