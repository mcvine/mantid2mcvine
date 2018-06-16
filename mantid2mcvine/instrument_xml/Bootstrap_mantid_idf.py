#
#  Jiao Lin
#


"""
Compose an instrument from mantid IDF xml file.

This implementation only uses the detector packs information
from mantid IDF. 

This is a base class.

XXX: should consider reading other information like moderator
XXX: and monitors from IDF as well.

XXX: coordinate system is now hard coded.

      <along-beam axis="z"/>
      <pointing-up axis="y"/>
      <handedness axis="right"/>

"""

import numpy as np

from .BootstrapBase import InstrumentFactory as base, PackInfo, units

# example tube_info
class TubeInfo:
    pressure = 10.*units.pressure.atm
    radius = .5 * units.length.inch
    gap = 0.08 * units.length.inch


class InstrumentFactory(base):
    
    def construct( 
            self, name, idfpath,
            ds_shape,
            xmloutput = None,
            mantid_idf_row_typename_postfix = None,
            mantid_idf_monitor_tag = None,
    ):
        
        # default output file
        if not xmloutput:
            import os
            base = os.path.basename(idfpath)
            fn = os.path.splitext(base)[0]
            xmloutput = '%s-danse.xml' % (fn,)

        # get packs from nexus file
        packs = self._readPacks(
            idfpath,
            mantid_idf_row_typename_postfix or 'detectors',
            mantid_idf_monitor_tag or 'monitors')
        return super(InstrumentFactory, self).construct(
            name, ds_shape, packs, xmloutput=xmloutput)


    def _readPacks(self, idfpath, mantid_idf_row_typename_postfix=None, mantid_idf_monitor_tag=None):
        raise NotImplementedError("_readPacks")
    

def getPositionAndOrientation(component):
    location = component.getChildren('location')[0]
    x = float(location.x); y = float(location.y); z = float(location.z)
    # pos = x,y,z
    # unit: mm
    pos = x*1000, y*1000, z*1000

    parent = location; rots = []
    while True:
        rot_elems = parent.getChildren('rot')
        if not rot_elems: break
        this = rot_elems[0]
        rots.append(getRotation(this))
        parent = this
        continue
    # rotate pack around vertical axis by 180 degree
    # rots.append(([0.,1.,0.], 180.))
    # rots.insert(0, ([0.,1.,0.], 180.))
    # rotate pack around beam by 180 degrees
    # rots.append(([0.,0.,1.], 180.))
    # rots.insert(0, ([0.,0.,1.], 180.))
    m = toMatrix(rots)
    angles = mr.toAngles(m)
    print "Position: %s, Rotation: inputs=%s, m=%s" % (pos, rots, m)
    return pos,angles


from mcni.neutron_coordinates_transformers import mcstasRotations as mr
def toMatrix(rots):
    # if len(rots)>2:
    #     import pdb; pdb.set_trace()
    rots.reverse()
    mats = map(rot2mat, rots)
    return reduce(np.dot, mats)

def getRotation(rot):
    axis = rot['axis-x'], rot['axis-y'], rot['axis-z']
    axis = map(float, axis)
    angle = float(rot['val'])
    return axis, angle

def rot2mat(rot):
    "assume rot is always along x or y or z"
    axis, angle = rot
    x = [1., 0., 0.]
    y = [0., 1., 0.]
    z = [0., 0., 1.]
    toM = mr.toMatrix
    # convert from mcstas convention to IS convention
    if axis == x: 
        return toM(angle, 0, 0)
    elif axis == y:
        return toM(0, angle, 0)
    elif axis == z:
        return toM(0, 0, angle)
    

# End of file
