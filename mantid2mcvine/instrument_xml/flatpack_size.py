# this script calculates the size of a N-pack
# the pack is assumed to be flat

from pyre.units.length import *
import numpy as np


def getSize( radius, height, gap, tube_positions ):
    # x is in pack plane
    # z is perpendicular to the pack plane
    # x is width, z is thickness
    #
    # unwrap
    tube_positions, unit = tube_positions
    tube_positions = np.array(tube_positions)
    # thickness is diff of min and max z plus edges
    zs = tube_positions[:, 2]
    thickness = (np.max(zs) - np.min(zs))*unit + radius * 2 + gap*2
    # similar for width
    xs = tube_positions[:, 0]
    width = (np.max(xs) - np.min(xs))*unit + radius * 2 + gap*2
    #
    with_cushion = 1.005
    size = {
        'thickness': thickness*with_cushion,
        'width': width * with_cushion,
        'height': height * with_cushion,
        }
    return size


if __name__ == '__main__':
    #radius of tube:
    radius = 0.5 *inch
    #height of tube:
    height = 1 *meter
    #gap between two tubes
    delta = 0.08 * inch
    print getSize( radius, height, delta )
