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
            instrument_name='myinstrument', beamline=9999999999,
            mantid_idf="myinstrument_Definition.xml",
            mcvine_idf='myinstrument_mcvine.xml', template_nxs ='myinstrument_template.nxs',
            detsys_shape=None,
            nmonitors = None,
            tofbinsize = 0.1,
            mantid_idf_row_typename_postfix = None,
            mantid_idf_monitor_tag = None,
            instrument_factory = None,
            ntotpixels = None,
            nbanks = None, ntubesperpack=None, npixelspertube=None,
    ):
        """Instrument model data object

        Parameters:
        -----------
        instrument_name : str
            name of the instrument. should be consistent with the instrument name in the input mantid IDF filename

        beamline: int
            beamline number

        mantid_idf: str
            input mantid IDF path

        mcvine_idf: str
            output mcvine IDF path

        template_nxs: str
            output NXS template file path

        detsys_shape: object
            instrument.geometry.shapes.{Shape} instance

        mantid_idf_row_typename_postfix: str
            This postfix string is used to search for all detector rows in the mantid IDF xml file.
            default is "detectors". For ARCS and SEQUOIA, it should be "row".

        mantid_idf_monitor_tag: str

        instrument_factory: instrument factory

        ntotpixels: total number of pixels

        nbanks, ntubesperpack, npixelspertube: for backward compatibility. used to compute ntotpixels
        """
        self.instrument_name = instrument_name
        self.beamline = beamline
        self.mantid_idf = os.path.abspath(mantid_idf)
        self.mcvine_idf = os.path.abspath(mcvine_idf)
        self.template_nxs = os.path.abspath(template_nxs)
        self.detsys_shape = detsys_shape
        self.nmonitors = nmonitors
        self.tofbinsize = tofbinsize
        self.mantid_idf_row_typename_postfix = mantid_idf_row_typename_postfix
        self.mantid_idf_monitor_tag = mantid_idf_monitor_tag
        from .instrument_xml.Bootstrap_mantid_idf_SNS_DGS import InstrumentFactory as default_IF
        self.instrument_factory = instrument_factory or default_IF
        self.ntotpixels = ntotpixels
        # backward compatibility
        if nbanks is not None and ntotpixels is None:
            self.ntotpixels = nbanks*ntubesperpack*npixelspertube
        return

    def convert(self):
        # print ntotpixels
        # create mcvine idf
        factory = self.instrument_factory()
        from instrument.geometry import shapes
        #   detsys_shape = shapes.hollowCylinder(in_radius=2., out_radius=3., height=3.)
        instrument, geometer = factory.construct(
            name=self.instrument_name, idfpath=self.mantid_idf,
            ds_shape = self.detsys_shape,
            xmloutput=self.mcvine_idf,
            mantid_idf_row_typename_postfix=self.mantid_idf_row_typename_postfix,
            mantid_idf_monitor_tag=self.mantid_idf_monitor_tag,
        )
        self.ntotpixels = ntotpixels = factory.ntotpixels
        # check number of monitors
        nmonitors = len(factory.parsed_instrument.monitor_locations)
        if self.nmonitors is not None:
            if self.nmonitors != nmonitors:
                import warnings
                warnings.warn("Number of monitors (%s) supplied is not consistent with number of monitors (%s) in IDF %s" % (
                    self.nmonitors, nmonitors, self.mantid_idf))
        else:
            self.nmonitors = nmonitors
        # create template nxs file
        from .nxs import template
        template.create(self.mantid_idf, ntotpixels, self.template_nxs, workdir='template_nxs_work')
        return

    def mantid_install(self, target=None):
        """install mantid IDF and adjust facilities.xml

        Parameters:
        -----------
        target : str
            if target is None, changes are made to user home directory.
            if target is a path, it must be the "instrument" directory where instrument IDFs are
        """
        # install mantid idf
        from . import instrument_xml
        instrument_xml.install_mantid_xml_to_userhome(self.mantid_idf, beamline=self.beamline, mantid_instr_dir=target)
        return

    def neutrons2events(self, scattered_neutrons, nodes=10, workdir='n2e', **kwds):
        from .nxs import Neutrons2Events
        n2e = Neutrons2Events.Neutrons2Events(
                instrument_xml=self.mcvine_idf,
                tofbinsize=self.tofbinsize)
        n2e.run(scattered_neutrons, workdir, nodes, **kwds)
        return os.path.join(workdir, 'out', 'events.dat')

    def events2nxs(self, events_dat, sim_nxs):
        from .nxs import Events2Nxs
        e2nxs = Events2Nxs.Event2Nxs(
            npixels = self.ntotpixels,
            nmonitors=self.nmonitors,
            nxs_template=self.template_nxs)
        e2nxs.run(eventfile=events_dat, nxsfile=sim_nxs, tofbinsize=self.tofbinsize)
        return sim_nxs

    def todict(self):
        keys = "instrument_name beamline mantid_idf mcvine_idf template_nxs ntotpixels"
        keys += " nmonitors tofbinsize"
        keys = keys.split()
        d = dict()
        for k in keys: d[k] = getattr(self, k)
        return d
