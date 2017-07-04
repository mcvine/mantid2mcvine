#!/usr/bin/env python

"""
From Mantid xml file, generate mcvine xml file for CHESS instrument
"""

from Bootstrap_mantid_idf import InstrumentFactory as IF

factory = IF()
factory.construct("mantid.xml")
