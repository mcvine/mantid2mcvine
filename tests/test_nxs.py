#!/usr/bin/env python

# local imports
from mantid2mcvine.nxs import template

# third party imports
import h5py
import numpy as np
from numpy.testing import assert_allclose

# standard imports
import os
import unittest


class Test(unittest.TestCase):

    def test_create_template(self):
        instrument_template = os.path.join(os.path.dirname(template.__file__), "start.nxs")
        here = os.path.dirname(__file__)
        idf = os.path.join(here, 'instrument_xml/xxxxMCVINETESTxxxx_Definition.xml')
        ntotpixels = 1024
        outpath = os.path.join(here, 'template.nxs')
        template.create(idf, ntotpixels, outpath,
                        workdir=os.path.join(here, 'work'),
                        instrument_template=instrument_template)

        # Check the modified contents of `outpath`
        with h5py.File(outpath, 'r') as f:
            ew = f['mantid_workspace_1']['event_workspace']
            assert_allclose(ew['axis1'][:], [-1.0, 16667.0], atol=0.1)
            assert_allclose(ew['axis2'], np.arange(1, ntotpixels + 1), atol=0.1)
            attrs = ew['axis2'].attrs
            for label, value in [('caption', 'Spectrum'), ('label', ''), ('units', 'spectraNumber')]:
                assert attrs[label].decode('utf-8') == value
            for entry in ['indices', 'pulsetime', 'tof']:
                assert entry not in ew
            f.close()
            pass


if __name__ == '__main__':
    unittest.main()
