#!/usr/bin/env python

import unittest
import os, shutil, glob

class Test(unittest.TestCase):

    def test_create_template(self):
        from mantid2mcvine.nxs import template
        idf = 'instrument_xml/MCVINETEST_Definition.xml'
        ntotpixels = 1024
        outpath = 'template.nxs'
        template.create(idf, ntotpixels, outpath, workdir='work')
        return



if __name__ =='__main__': unittest.main()
    
