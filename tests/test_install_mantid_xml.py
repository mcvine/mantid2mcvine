#!/usr/bin/env python

import unittest
import os, shutil, glob

class Test(unittest.TestCase):

    def test(self):
        here = os.path.dirname(__file__)
        from mantid2mcvine import instrument_xml
        install = instrument_xml.install_mantid_xml_to_userhome
        # save the original one
        path = os.path.expanduser('~/.mantid/instrument/Facilities.xml')
        saved = os.path.join(here, './instrument_xml/saved_Facilities.xml')
        shutil.copyfile(path, saved)
        try:
            # add example Facilities.xml file for testing
            shutil.copyfile(os.path.join(here, './instrument_xml/Facilities.xml'), path)
            # tests
            # 1. first install
            install(os.path.join(here, './instrument_xml/xxxxMCVINETESTxxxx_Definition.xml'))
            # 2. install same file
            try:
                install(os.path.join(here, './instrument_xml/xxxxMCVINETESTxxxx_Definition.xml'))
            except instrument_xml.DefinitionExists:
                pass
            else:
                raise RuntimeError("Expect DefinitionExists error")
            # 3. install a file at the same beamline
            try:
                install(os.path.join(here, './instrument_xml/xxxxMCVINETESTxxxx2_Definition.xml'))
            except instrument_xml.BeamlineOccupied:
                pass
            else:
                raise RuntimeError("Expect BeamlineOccupied error")
            # 4. install at different beamline
            install(os.path.join(here, './instrument_xml/xxxxMCVINETESTxxxx2_Definition.xml'), 100)
            # 5. install a different version
            install(os.path.join(here, './instrument_xml/xxxxMCVINETESTxxxx_Definition_2016.xml'))
        finally:
            # clean up
            shutil.copyfile(saved, path)
            for f in glob.glob(os.path.expanduser('~/.mantid/instrument/xxxxMCVINETESTxxxx*_Definition*.xml')):
                os.remove(f)
        return


if __name__ =='__main__': unittest.main()
