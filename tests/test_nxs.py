#!/usr/bin/env python

import unittest
import os, shutil, glob

class Test(unittest.TestCase):

    def test_create_template(self):
        here = os.path.dirname(__file__)
        from mantid2mcvine.nxs import template
        idf = os.path.join(here, 'instrument_xml/xxxxMCVINETESTxxxx_Definition.xml')
        ntotpixels = 1024
        outpath = os.path.join(here, 'template.nxs')
        template.create(idf, ntotpixels, outpath, workdir=os.path.join(here, 'work'))
        return



if __name__ =='__main__': unittest.main()
    
