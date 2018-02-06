from ._version import __version__

import os

from .instrument_xml.Bootstrap_mantid_idf import units
from instrument.geometry import shapes

class TubeInfo:

    def __init__(self, pressure=None, radius=None, gap=None):
        self.pressure = pressure if pressure is not None else 10.*units.pressure.atm
        self.radius = radius if radius is not None else .5 * units.length.inch
        self.gap = gap if gap is not None else 0.08 * units.length.inch
        return


class InstrumentModel:

    def __init__(
            self,
            instrument_name, beamline, mantid_idf, mcvine_idf, template_nxs,
            detsys_shape, tube_info,
            nbanks = 1,
            ntubesperpack = 8,
            npixelspertube = 128,
            nmonitors = 1,
            tofbinsize = 0.1,
    ):
        self.instrument_name = instrument_name
        self.beamline = beamline
        self.mantid_idf = mantid_idf
        self.mcvine_idf = mcvine_idf
        self.template_nxs = template_nxs
        self.detsys_shape = detsys_shape
        self.tube_info = tube_info
        self.nbanks = nbanks
        self.ntubesperpack = ntubesperpack
        self.npixelspertube = npixelspertube
        self.nmonitors = nmonitors
        self.tofbinsize = tofbinsize
        return
    
    def convert(self):
        ntotpixels = self.nbanks*self.ntubesperpack*self.npixelspertube
        # print ntotpixels
        # install mantid idf
        from . import instrument_xml
        instrument_xml.install_mantid_xml_to_userhome(self.mantid_idf, beamline=self.beamline)
        # create mcvine idf
        from .instrument_xml.Bootstrap_mantid_idf import InstrumentFactory as IF
        factory = IF()
        from instrument.geometry import shapes
        #   detsys_shape = shapes.hollowCylinder(in_radius=2., out_radius=3., height=3.)
        instrument, geometer = factory.construct(
            name=self.instrument_name, idfpath=self.mantid_idf,
            ds_shape = self.detsys_shape, tube_info=self.tube_info,
            xmloutput=self.mcvine_idf)
        # create template nxs file
        from .nxs import template
        template.create(self.mantid_idf, ntotpixels, self.template_nxs, workdir='template_nxs_work')
        return


    def neutrons2events(self, scattered_neutrons, nodes=10, workdir='n2e'):
        from .nxs import Neutrons2Events
        n2e = Neutrons2Events.Neutrons2Events(
                instrument_xml=self.mcvine_idf,
                tofbinsize=self.tofbinsize)
        n2e.run(scattered_neutrons, workdir, nodes)
        return os.path.join(workdir, 'out', 'events.dat')


    def events2nxs(self, events_dat, sim_nxs):
        from .nxs import Events2Nxs
        e2nxs = Events2Nxs.Event2Nxs(
            nbanks=self.nbanks, npixelspertube=self.npixelspertube,
            ntubesperpack=self.ntubesperpack, nmonitors=self.nmonitors,
            nxs_template=self.template_nxs)
        e2nxs.run(eventfile=events_dat, nxsfile=sim_nxs, tofbinsize=self.tofbinsize)
        return sim_nxs
