#!/usr/bin/env python

import os
import mantid2mcvine as m2m
import instrument.geometry.operations

instrument_name = 'MARI_virtual'
beamline =  997
mantid_idf = os.path.abspath('./MARI_virtual_Definition.xml')
mcvine_idf = os.path.abspath('MARI_mcvine.xml')
template_nxs = os.path.abspath('MARI_template.nxs')

cyl = m2m.shapes.hollowCylinder(in_radius=3., out_radius=5., height=3.) # meters
detsys_shape = instrument.geometry.operations.rotate(cyl, axis=(1,0,0), angle=90.)
nbanks = 1
ntubesperpack = 8
npixelspertube = 128
nmonitors = 1

tube_info = m2m.TubeInfo(
    pressure = 10.*m2m.units.pressure.atm,
    radius = .5 * m2m.units.length.inch,
    gap = 0.08 * m2m.units.length.inch,
)

tofbinsize = 0.1 # mus

import unittest
import os

class Test(unittest.TestCase):

    def test_create_template(self):
        here = os.path.dirname(__file__)
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
        self.assert_(xml_equal(out, expected))
        return

    def _test(self):
        im = m2m.InstrumentModel(
            instrument_name, beamline, mantid_idf, mcvine_idf, template_nxs,
            detsys_shape, tube_info,
            nbanks = nbanks,
            ntubesperpack = ntubesperpack,
            npixelspertube = npixelspertube,
            nmonitors = nmonitors,
            tofbinsize = tofbinsize,
            mantid_idf_row_typename_postfix = 'bank',
            mantid_idf_monitor_tag = 'monitor',
        )

        im.convert()
        # im.mantid_install() # install mantid IDF to ~/.mantid
        return


if __name__ =='__main__': unittest.main()
