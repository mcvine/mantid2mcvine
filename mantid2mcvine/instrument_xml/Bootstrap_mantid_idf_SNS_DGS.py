#
#  Jiao Lin
#


"""
Compose an instrument from mantid IDF xml file for a SNS DGS instrument.

This inherits from Bootstrap_mantid_idf.
"""

import numpy as np

from .Bootstrap_mantid_idf import InstrumentFactory as base, getPositionAndOrientation, units, PackInfo
from .BootstrapBase import shapes
units_parser = units.parser()
units_parser.context.update(metre=units.length.meter)

class InstrumentFactory(base):
    
    def _readPacks(self, idfpath, mantid_idf_row_typename_postfix=None, mantid_idf_monitor_tag=None):
        from instrument.mantid import parse_file
        self.parsed_instrument = inst = parse_file(
            idfpath,
            rowtypename=mantid_idf_row_typename_postfix,
            monitortag=mantid_idf_monitor_tag)

        # extract tube info
        # XXX assume all tubes have the same pressure
        
        import operator as op
        rows = inst.detectors
        getpacks = lambda row: row.getType().components
        packs = [getpacks(row) for row in rows]
        packs = reduce(op.add, packs)
        
        for pkno, pkinfo in enumerate(packs):
            # pkinfo: instance of instrument.mantid.component
            typename = pkinfo.type
            pack_comp = pkinfo.getType().components[0]  # wrapper of mantid IDF pack <component> tag
            pack_type = pack_comp.getType()             # wrapper of mantid IDF pack <type> tag
            ntubes = getNTubes(pack_type)
            npixels = getNPixelsPerTube(pack_type)
            position, orientation = getPositionAndOrientation(pack_comp)
            tubelen = getTubeLength(pack_type)
            tube_positions = getTubePositions(pack_type)
            
            pack = PackInfo()
            pack.typename = typename
            pack.id = pkno
            pack.position = position 
            pack.orientation = orientation
            pack.ntubes = ntubes
            pack.npixelspertube = npixels
            pack.tubelength = tubelen * 1000

            tubes, pixels = getTubeParameters(inst)
            # tubes and pixels are info extracted from mantid xml
            # Each detector row has one entry in tubes
            # for now we just use one entry
            # tubes:
            # {'detectors': {
            #     'tube_pressure': '10.0 * atm',
            #     'tube_thickness': '0.001016 * metre',
            #     'tube_temperature': '292.0 * K'}
            # }
            # Each kind of pixel has one try in `pixels`
            # For now we only care about pixel radius and assume all pixels have the
            # same radius
            # pixels:
            # {'pixel': {'radius': 12.7, 'height': 11.719}}
            pack.pressure = units_parser.parse(tubes.values()[0]['tube_pressure'])/units.pressure.atm
            pack.tuberadius = pixels.values()[0]['radius']
            # gap is used to compute pack size only
            pack.tubegap = units_parser.parse(tubes.values()[0]['tube_thickness'])*2/units.length.mm
            # tube positions
            tp = tube_positions*1000
            pack.tube_positions = tuple([ tuple(a) for a in tp ])
            # create pack shape
            from .flatpack_size import getSize
            mm = units.length.mm
            pack.shape = shapes.block(**getSize(
                pack.tuberadius*mm, pack.tubelength*mm, pack.tubegap*mm, (tp, units.length.mm)))
            yield pack
            continue
        
        return


def getTubeParameters(instrument):
    """extract parameters (pressure, radius, etc) from instrument xml node

instrument is an instance of `instrument.mantid.instrument`

In <component-link name="{name}"> there are some parameters.
Each parameter is sth like

  <parameter name="tube_pressure">
    <value units="atm" val="10.0"/>
  </parameter>

In <type is="detector" name="pixel*"> we can obtain radius and height
    """
    # <component-link>
    tubes = dict()
    comp_links = instrument.getNodes('component-link')
    for cl in comp_links:
        name = cl.name
        params = cl.getChildren('parameter')
        res = dict()
        for p in params:
            name = p.name
            v = p.getChildren('value')[0]
            res[name] = '%s * %s' % (v.val, v.units)
            continue
        tubes[cl.name] = res
        continue
    # <type is..>
    pixels = dict()
    types = instrument.getNodes('type')
    for t in types:
        if t._node.attrib.get('is', None) != 'detector': continue
        name = t.name
        cyl = t.getChildren('cylinder')[0]
        radius = float(cyl.getChildren('radius')[0].val)*1000. # mm
        height = float(cyl.getChildren('height')[0].val)*1000. # mm
        pixels[name] = dict(radius=radius, height=height)
        continue
    return tubes, pixels


def getTubeLength(pack_type):
    tube = pack_type.components[0]
    tube_type = tube.getType()
    pixels = tube_type.components[0]
    locations = pixels.getChildren('location')
    y0 = float(locations[0].y)
    y_1 = float(locations[-1].y)
    n = len(locations)
    return (y_1-y0)/(n-1)*n


def getTubePositions(pack_type):
    tube = pack_type.components[0]
    locations = tube.getChildren('location')
    def _get(loc, a):
        try: return loc[a]
        except KeyError: return 0.
    xyz = [map(float, (_get(loc, 'x'), _get(loc, 'y'), _get(loc, 'z'))) for loc in locations]
    return np.array(xyz)


def getNTubes(pack_type):
    tube = pack_type.components[0]
    locations = tube.getChildren('location')
    return len(locations)


def getNPixelsPerTube(pack_type):
    tubes = pack_type.components[0]
    tube_type = tubes.getType()
    pixels = tube_type.components[0]
    locations = pixels.getChildren('location')
    return len(locations)


# End of file
