#!/usr/bin/env python

import unittest
import os, shutil, glob

class Test(unittest.TestCase):

    def test(self):
        from mantid2mcvine import nxs
        idf = 'instrument_xml/MCVINETEST_Definition.xml'
        ntotpixels = 1024
        outpath = 'template.nxs'
        nxs.create_template(idf, ntotpixels, outpath, workdir='work')
        return



if __name__ =='__main__': unittest.main()
    
