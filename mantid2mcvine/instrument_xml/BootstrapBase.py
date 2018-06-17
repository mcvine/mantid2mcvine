#!/usr/bin/env python
#
#                                   Jiao Lin
#

"""
This piece of code create a graph of instrument elements for a dgs instrument.
It is modified from ..CNCS.BootstrapBase.

The detector system is assumed to consist of packs. 
Each pack contains some detector tubes.
The tubes do not have to form a flat structure in a pack.

This is a base class to be extended.
"""

import numpy as np
from instrument.factories.CNCS.BootstrapBase import InstrumentFactory as base, PackInfo, units, elements, geometers, shapes, packType, pixelSolidAngle, m, mm, atm

class PackInfo:

    id = None
    shape = None
    position = None # unit: mm
    orientation = None # unit: degree
    pressure = None # unit: atm
    ntubes = None
    tubelength = None # unit: mm
    tuberadius = None # unit: mm
    tubegap = None # unit: mm
    npixelspertube = None
    tube_positions = None # unit: mm


def packType(packinfo):
    """return the signature of the detector pack. packs with the same signature are identical, but could differ in position and orientation
    """
    return packinfo.typename, packinfo.pressure, packinfo.ntubes, packinfo.tubelength, packinfo.tuberadius, packinfo.tubegap, packinfo.npixelspertube, packinfo.tube_positions


class InstrumentFactory( base ):
    
    """Use given detector info and
    hard-coded info to construct an
    Instrument object and a geometer"""


    def construct( 
            self, instrument_name, ds_shape, packs,
            xmloutput = None ):
        '''construct a new instrument

Parameters:
  - instrument_name: instrument name
  - ds_shape: detector system shape
  - packs: a list of PackInfo instances
'''
        self._instrument = instrument = elements.instrument(
            instrument_name )# version="0.0.0")
        
        #instrument local geometer
        geometer = geometers.geometer(
            instrument, registry_coordinate_system = 'McStas' )
        self.local_geometers = [geometer]
        
        # make Moderator
        # self.makeModerator( instrument, geometer )
        
        # make monitors: adds elements to instrument & geometer
        # self.makeMonitors( instrument, geometer, monitorRecords)
        
        #make sample
        sample = elements.sample(
            'sample',guid = instrument.getUniqueID() )
        instrument.addElement( sample )
        geometer.register( sample, (0*m,0*m,0*m), (0,0,0) ) 
        
        # make detector array: adds elements to instrument & geometer
        self.makeDetectorSystem(instrument, geometer, ds_shape, packs)
        
        # set up guid registry
        instrument.guidRegistry.registerAll( instrument )
        
        # instrument global geometer
        instrumentGeometer = geometers.arcs(
            instrument, self.local_geometers,
            registry_coordinate_system = 'McStas' )
        
        instrument.geometer = instrumentGeometer
        
        # clean up temporary variables
        del self.local_geometers, self._instrument
        
        # save the xml description
        if xmloutput:
            from instrument.nixml import weave
            print 'write instrument to %s' % xmloutput
            weave( instrument, open(xmloutput, 'w') )
        return instrument, instrumentGeometer
    
    
    def makeModerator( self, instrument, geometer):
        #hard code moderator. this should be ok because
        #it should not change
        modXSize = 100.0*mm; modYSize = 100.0*mm; modZSize = 100.0*mm
        position = [0* mm, 0*mm, 0*mm]
        orientation = [0.0, 0.0, 0.0]
        modID = instrument.getUniqueID()
        moderator = elements.moderator(
            'moderator', 
            modXSize, modYSize, modZSize,
            type = "non-existant",
            guid = modID,
            )
        
        instrument.addElement( moderator )
        geometer.register( moderator, position, orientation)
        return
    
    
    def makeMonitors( self, instrument, geometer, monitorRecords):
        #### not used right now ####
        i = 0
        
        for record in monitorRecords:
            monid = record['id']
            dist = record['distanceToModerator']
            position = [dist, 0 * mm, 0 * mm]
            name = "monitor%s" % i
            
            debug.log("monitor position: %s, monitor name: '%s', id: %s" %
                      (position, name, monid))
            
            dimensions = record['dimensions']
            width, height, thickness = dimensions
            
            monitor = elements.monitor(
                name, width, height, thickness,
                guid = instrument.getUniqueID() )
            
            instrument.addElement( monitor )
            i += 1
            
            geometer.register( monitor, position, orientation=[0.0,0.0,0.0])
            continue

        return


    def makeDetectorSystem( self, instrument, geometer, shape, packs):

        #detector system
        detSystem = elements.detectorSystem(
            'detSystem', shape, guid = instrument.getUniqueID())
        instrument.addElement( detSystem )
        geometer.register( detSystem, (0*m,0*m,0*m), (0,0,0),
                           relative = instrument.getSample() )
        
        detSystemGeometer = geometers.geometer(
            detSystem, registry_coordinate_system = 'McStas' )
        self.local_geometers.append( detSystemGeometer )
        
        from numpy import array
        
        cache = {}
        for packinfo in packs:
            
            rotation = packinfo.orientation
            translation = tuple(array( packinfo.position )*mm)
            
            packID = packinfo.id
            name = 'pack%s' % packID
            
            packtype = packType(packinfo)
            pack = cache.get(packtype)
            
            if pack is None:
                # typename, pressure, ntubes, height, radius, gap, npixels, tube_positions = \
                #    packtype

                pack = cache[packtype] = self._makePack(name, packID, instrument, packinfo)
                """
                    name, packID, instrument,
                    pressure*atm, npixels, radius*mm, height*mm, gap*mm,
                    (np.array(tube_positions), mm))
                """
                
            else:
                copy = elements.copy(
                    'pack%s' % packID, pack.guid(),
                    id = packID,
                    guid = instrument.getUniqueID() )
                pack = copy
                pass
            
            detSystem.addElement( pack )
            detSystemGeometer.register(
                pack, translation, rotation )

            continue

        return # detArray # instrument, geometer

    
    tube_orientation = (0, 0, 0)
    def _makePack(self, name, id, instrument, packinfo):
        '''make a unique N-pack
        
all physical parameters must have units attached.
'''
        pack = elements.detectorPack(
            name, shape = packinfo.shape, guid = instrument.getUniqueID(), id = id )
        packGeometer = geometers.geometer( pack, registry_coordinate_system='McStas' )
        self.local_geometers.append( packGeometer )

        # XXX this is not generic enough. tubes could be different in a pack
        det0 = self._makeDetector(
            'det0', 0, instrument, packinfo.pressure*atm, packinfo.npixelspertube, packinfo.tuberadius*mm, packinfo.tubelength*mm)
        pack.addElement( det0 )
        
        # unwrapping
        tube_positions = np.array(packinfo.tube_positions); unit=mm
        ntubes = tube_positions.shape[0]
        packGeometer.register( det0, tube_positions[0]*unit, self.tube_orientation)
        for i in range(1,ntubes):
            det = elements.copy( 'det%s' % i, det0.guid(), guid = instrument.getUniqueID() )
            pack.addElement( det )
            packGeometer.register( det, tube_positions[i]*unit, self.tube_orientation)
            continue
        return pack
    
    
    def _makeDetector(self, name, id, instrument, 
                      pressure, npixels, radius, height):
        '''make a unique detector module

all physical parameters must have units attached.
'''
        # from instrument.factories.LPSDFactory import create
        # detector, geometer = create(
        detector, geometer = createLPSD(
            name, id, 
            pressure, radius, height, npixels,
            pixelSolidAngle,
            instrument)
        self.local_geometers.append( geometer )
        return detector

    pass # end of InstrumentFactory


def createLPSD(
        name, id, 
        pressure, radius, height, npixels,
        pixelSolidAngle,
        guidGenerator,
        detectorFactory = None,
        pixelFactory = None,
        geometerFactory = None):
    '''make a unique detector module

all physical parameters must have units attached.
'''
    if detectorFactory is None:
        from instrument.elements import detector as detectorFactory
        pass

    if pixelFactory is None:
        from instrument.elements import pixel as pixelFactory
        pass

    if geometerFactory is None:
        from instrument.geometers import geometer as geometerFactory
        pass
    
    guid = guidGenerator.getUniqueID()

    # create detector itself
    detector = detectorFactory(
        name, 
        radius = radius, height = height, pressure = pressure,
        guid = guid, id = id,
        )

    # geometer for pixels in the detector
    detectorGeometer = geometerFactory( detector, registry_coordinate_system='McStas' )

    # now pixels
    #  first pixel
    #   pixel height
    pixelht = height / npixels
    # pixel must from down to up. this is a requirement from
    # instrument simulation
    bottom = (-(npixels)/2.0 + 0.5)*pixelht
    pixel0 = pixelFactory(
        'pixel0',
        radius = radius, height = pixelht, solidAngle = pixelSolidAngle,
        guid = guidGenerator.getUniqueID(),
        )
    detector.addElement( pixel0 )
    detectorGeometer.register( pixel0, (0*pixelht,bottom,0*pixelht), (0,0,0) )

    #  all other pixels are copies of the first pixel
    from instrument.elements import copy
    for i in range(1, npixels):
        pixel = copy( 'pixel%s' % i, reference = pixel0.guid(),
                      guid = guidGenerator.getUniqueID() )
        z = bottom + i*pixelht
        detector.addElement( pixel )
        detectorGeometer.register( pixel, (0*pixelht,z,0*pixelht), (0,0,0) )
        continue
    
    return detector, detectorGeometer


# End of file
