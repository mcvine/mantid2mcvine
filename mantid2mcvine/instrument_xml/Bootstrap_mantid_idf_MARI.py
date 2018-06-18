#
#  Jiao Lin
#


"""
Compose an instrument from mantid IDF xml file for a SNS DGS instrument.

This inherits from Bootstrap_mantid_idf.
"""

import numpy as np, copy

from .Bootstrap_mantid_idf import InstrumentFactory as base, getPositionAndOrientation, units, PackInfo, TubeInfo
from instrument.geometry import shapes, operations
units_parser = units.parser()
units_parser.context.update(metre=units.length.meter)

class InstrumentFactory(base):
    
    def _readPacks(self, idfpath, mantid_idf_row_typename_postfix=None, mantid_idf_monitor_tag=None):
        from instrument.mantid import parse_file
        self.parsed_instrument = inst = parse_file(
            idfpath,
            rowtypename=mantid_idf_row_typename_postfix,
            monitortag=mantid_idf_monitor_tag)

        # global tube attributes
        # comp_links is like
        # {'MARI_virtual':
        #     {'TubeThickness': '0.0008 * metre', 'TubePressure': '10.0 * atm',
        #      'DelayTime': '-3.9 *microseconds'},
        #  'monitor': {'DelayTime': '0 * microseconds'}
        # }
        comp_links = getComponentLinks(inst)
        tube_params = comp_links[inst._root.attrib['name']]
        tube_pressure = units_parser.parse(tube_params['TubePressure'])/units.pressure.atm
        tube_gap = units_parser.parse(tube_params['TubeThickness'])*2/units.length.mm
        #
        # get all packs
        import operator as op
        rows = inst.detectors
        getpacks = lambda row: row.getType().components
        packs = [getpacks(row) for row in rows]
        packs = reduce(op.add, packs)
        #
        # loop over packs
        for pkno, pkinfo in enumerate(packs):
            # pkinfo: instance of instrument.mantid.component
            pack_type = pkinfo.getType()
            typename = pack_type.name
            if typename != 'W1-1': continue
            comps = pack_type.getChildren('component') # instance of instance.mantid.component
            # tubeinfo list for this pack
            tubeinfos = []
            for comp in comps:
                # comp is an instance of instrument.mantid.component
                # representing a tag like <component type="tall He3 element">
                tubetypename = comp.type
                tubeinfo = TubeInfo()
                tube_type = comp.getType() # instance of instance.mantid.node
                tubeinfo.typename = tubetypename
                tubeinfo.pressure = tube_pressure
                tubeinfo.gap = tube_gap # gap is used to compute pack size only
                geom_info = getTubeGeomInfo(tube_type)
                tubeinfo.radius = geom_info['radius']
                tubeinfo.length = geom_info['height']
                tubeinfo.npixels = 1 # not pixellated
                # this comp have multiple locations
                for loc in comp.getChildren('location'):
                    _ = copy.copy(tubeinfo)
                    _.position, _.orientation = computePositionAndOrientation(loc)
                    tubeinfos.append(_)
                continue
            
            pack = PackInfo()
            pack.typename = typename
            pack.id = pkno
            pack.tubes = tubeinfos
            # very different from SNS DGS instruments,
            # the pack is placed at origin
            pack.position = [0., 0., 0.]
            pack.orientation = [0., 0., 0.]
            pack.ntubes = len(tubeinfos)
            # 
            # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            # create pack shape
            # import pdb; pdb.set_trace()
            pack.shape = computePackShape(pack)
            yield pack
            continue
        
        return

def computePackShape(pack):
    # pack shape is a partial hollow cylinder with its origin at the sample position
    # The axis of cylinder is the same as the tube axis, determined by tube.rot_z
    # so we can just use the same rotation to rotate the cylinder
    # The top and the bottom of the cylinder can be computed from the top and bottom
    # positions of one of the longer tubes.
    # Then we can know the height of the cylinder.
    # The inner and outer radii can be calculated as tube.loc.r \pm tube.radius.
    # The start and end angles of the opening (to be formed by an intersection
    # with a pyramid) can be calculated using positions of first and last tubes
    #
    # rotate(translate(intersect(
    #     hollowCylinder(in_radius, out_radius, h),
    #     pyramid()
    #   ),
    #   [0, center_y, 0]),
    #   (0,0,rz))
    #
    tube0 = pack.tubes[0]
    rx, ry, rz = tube0.orientation
    assert rx==0 and ry==0
    # the orientation of the hollow cyl would be just rotate `rz` angle about z
    #
    # rotation matrix that converts coordinates of a vector to the rotated frame
    # np.dot(rotmat, v_in_orig_frame) --> v_in_new_frame
    rotmat = np.array([
        [np.cos(rz), np.sin(rz), 0],
        [-np.sin(rz), np.cos(rz), 0],
        [0, 0, 1.]])
    # find longest tube and max tube radius
    longest = 0; max_tube_r = 0
    for tube in pack.tubes:
        assert tube.orientation == tube0.orientation
        if tube.length > longest: longest = tube.length
        if tube.radius > max_tube_r: max_tube_r = tube.radius
        continue
    longest/=1000.; max_tube_r/=1000.  # meter
    height = longest*1.05
    # y offset of the hollow cylinder. now offset along x and z
    centers = np.array([np.dot(rotmat, tube.position) for tube in pack.tubes])
    center_ys = [c[1] for c in centers]
    center_y = np.mean(center_ys)
    for y1 in center_ys: assert(abs(y1-center_y)<0.0005)
    # radius of the hollow cyl
    radii = (centers[:, 0] **2 + centers[:, 2]**2)**.5
    radius = np.mean(radii)
    for r in radii: assert(abs(radius-r)<0.0005)
    # in and out radius
    in_radius = radius - max_tube_r * 1.05
    out_radius = radius + max_tube_r * 1.05
    # now we can create the cylinder
    meter = units.length.meter
    hollow_cyl = operations.subtract(
        shapes.cylinder(out_radius*meter, height*meter),
        shapes.cylinder(in_radius*meter, height*2*meter))
    # start and end angles
    tube_angles = np.arctan2(centers[:,0], centers[:, 2])
    min = np.min(tube_angles); max = np.max(tube_angles)
    step = (max-min)/len(tube_angles)
    min_angle = min - step; max_angle = max + step; angle_span = max_angle - min_angle
    mid_angle = (min_angle+max_angle)/2.
    # the angle above is angle rotated from beam.
    # original orientatin of a pyramid is vertical. Its tip is at origin
    # need to first rotate the pyramid around x by -90.
    # then rotate around the y axis by whatever angle needed
    # the "thickness" would actually be the height of the tubes
    # the "width" would be to cover the whole angle range between min_angle and max_angle
    # the "height" can be chosen to be a bit larger than the out-radius of the hollow cylinder
    pyr_height = out_radius*1.2
    pyr_width =2* pyr_height*np.tan(angle_span/2)
    pyr = shapes.pyramid(thickness=height*1.05*meter, height=pyr_height*meter, width=pyr_width*meter)
    # rotated pyramid
    rotated_pyr = operations.rotate(
        operations.rotate(pyr, transversal=1., angle='-90.*deg'),
        vertical=1., angle='%s*deg' % np.rad2deg(mid_angle))
    #
    intersection = operations.intersect(hollow_cyl, rotated_pyr)
    return operations.rotate(
        operations.translate(intersection, vertical=center_y*meter),
        beam=1., angle='%s*deg' % np.rad2deg(rz))
    
    
def computePositionAndOrientation(loc):
    r = float(loc.r)
    theta = np.deg2rad(float(loc.t))
    phi = np.deg2rad(float(loc.p))
    from numpy import sin, cos
    position = r*sin(theta)*cos(phi), r*sin(theta)*sin(phi), r*cos(theta)
    #
    rotz = np.deg2rad(float(loc.rot))
    orientation = (0., 0., rotz)
    return position, orientation

def getComponentLinks(instrument):
    """extract parameters (pressure, thickness, etc) from instrument xml node

instrument is an instance of `instrument.mantid.instrument`

In <component-link name="{name}"> there are some parameters.
Each parameter is sth like

  <parameter name="tube_pressure">
    <value units="atm" val="10.0"/>
  </parameter>

    """
    # <component-link>
    info = dict()
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
        info[cl.name] = res
        continue
    return info


def getTubeGeomInfo(tubetype):
    # tubetype is an instance of instrument.mantid.node
    cyl = tubetype.getChildren('cylinder')[0]
    # axis of tube is also in "cyl", but we ignore it for now
    radius = float(cyl.getChildren('radius')[0].val)*1000. # mm
    height = float(cyl.getChildren('height')[0].val)*1000. # mm
    return dict(radius=radius, height=height)

# End of file
