# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
# Inital version October 2010
#
# This file is part of casata and is licensed under GPL version 2
"""
Simple example of how to compute the baseline errors from phase errors
"""

import numpy

import casata, casata.tools
from casata.tools import ctools, vtasks, calibration, data

def cvPhase(d):
    """
    Return the phase of the complex array d
    """
    return numpy.arctan2(d.imag, d.real)

def obsBaselineData(msin,
                    a1, a2,
                    spw,
                    warndrift=1e-2):
    """
    Compute the phase variation between scans 

    :param a1, a2: Consider the baseline between these two antennas

    :returns: list of tuples (azimuth, elevation, phase, phasrms)
    """
    res=[]
    for sno in data.scans(msin):
        d=data.vis(msin,
                   ["DATA", "TARGET"], 
                   a1=a1, a2=a2, 
                   spw=spw, 
                   scan=sno)
        ph=cvPhase(d[0][0,0])
        if d[1][0].std() > warndrift or d[1][1].std() > warndrift:
            print "Antennas seem to have moved a lot during scan %i " % sno
        res.append( (d[1][0].mean(),
                     d[1][1].mean(),
                     ph.mean(),
                     ph.std()))
    return res

def calcDirCos(az, el):
    """
    Calculate the direction cosines
    
    :returns: X (east), Y(north), Z(up)
    """
    return (numpy.sin(az)*numpy.cos(el),
            numpy.cos(az)*numpy.cos(el),
            numpy.sin(el))

def baselineSolve(obsdata,
                  wavel):
    """
    This returns the offsets in the antenna coordinate system.
    
    Note that the weighting (as in phaserms) is not yet included
    """
    m=numpy.array([calcDirCos(x[0], x[1]) for x in obsdata])
    b=numpy.array([x[2] for x in obsdata])
    x=numpy.linalg.lstsq(m, b)[0]
    return x*wavel/(2*math.pi);


    
                     
                     
