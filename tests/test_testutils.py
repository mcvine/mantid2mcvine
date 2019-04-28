#!/usr/bin/env python

import unittest
import os, shutil, glob
from mantid2mcvine import testutils

class Test(unittest.TestCase):

    def test_equal_quantity(self):
        testutils.test_equal_quantity()
        return



if __name__ =='__main__': unittest.main()
    
