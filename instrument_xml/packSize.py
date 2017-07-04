# modified from CNCS: height is 1 meter

#this little script calculates the size of a 8-pack
#
from pyre.units.length import *
import numpy as np

#radius of tube:
radius = 0.5 *inch
#height of tube:
height = 1 *meter
#gap between two tubes
delta = 0.08 * inch



def getSize( radius, height, gap, tube_positions ):
    # unwrapping
    tube_positions, unit = tube_positions
        
    # x is in pack plane
    # z is perpendicular to the pack plane
    # x is width, z is thickness

    # thickness is diff of min and max z plus edges
    zs = tube_positions[:, 2]
    thickness = (np.max(zs) - np.min(zs))*unit + radius * 2 + gap*2
    # similar for width
    xs = tube_positions[:, 0]
    width = (np.max(xs) - np.min(xs))*unit + radius * 2 + gap*2
    
    with_cushion = 1.005
    size = {
        'thickness': thickness*with_cushion,
        'width': width * with_cushion,
        'height': height * with_cushion,
        }
    return size

if __name__ == '__main__':
    print getSize( radius, height, delta )
