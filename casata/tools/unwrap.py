# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>, <bojan@bnikolic.co.uk>
# Original version 2007.  Originally in smatools.py, then in the
# ALMAWVR repository
#
# This file is part of the ALMA WVR analysis library and is licensed
# under GPL V2
"""
Tools for unwrapping phases
"""

import math
import numpy

def phase(ph, maxstep):
    """
    Unwrap a sequence of phase measurements
    
    :param maxstep: The maximum step size, if a step greater than this
    is found assume it is due to a wrap

    The user should determine the maxstep parameter by considering the
    histogram of phase changes.
    """
    # phase steps
    # deltaph= ph[1:] - ph[:-1]
    x=numpy.zeros(len(ph),
                  numpy.float64)
    x[0]=ph[0]
    turns=0
    for i in range(1,len(ph)):
        step=ph[i]-ph[i-1]
        if math.fabs( step ) > maxstep:
            #looks like a wrap            
            if ( step  > 0) :
                # a large forward jump in phase ... must have wound
                # through -180
                turns -= 1
            else:
                # large backward jump ... must have gone through +180                
                turns += 1
        x[i]=ph[i] + turns * 360
    return x

