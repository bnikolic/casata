# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
# Inital version October 2010
#
# This file is part of casata and is licensed under GPL version 2
"""
Simple example of how to compute the baseline errors from phase errors
"""

import math
import numpy

import casata, casata.tools
from casata.tools import ctools, vtasks, calibration, data

def cvPhase(d):
    """
    Return the phase of the complex array d
    """
    return numpy.arctan2(d.imag, d.real)

def getPhases(caltable,
              antno):
    """
    Get phases for each scan in caltable  for antenna antno
    """
    s, g=data.cal(caltable, 
                  ["FIELD_ID", "GAIN"], 
                  a1=antno)
    return s+1, cvPhase(g[0,0])
    

def calcDirCos(az, el):
    """
    Calculate the direction cosines
    
    :returns: X (east), Y(north), Z(up)
    """
    return (numpy.sin(az)*numpy.cos(el),
            numpy.cos(az)*numpy.cos(el),
            numpy.sin(el))

def scanDirCos(msin,
               warndrift=1e-2):
    """
    Dictionary of direction cosines of each scan in the observation
    """
    res={}
    for sno in data.scans(msin):
        d=data.vis(msin,
                   ["TARGET"], 
                   a1=0, 
                   a2=0, 
                   spw=0, 
                   scan=sno)
        if d[0][0].std() > warndrift or d[0][1].std() > warndrift:
            print "Antennas seem to have moved a lot during scan %i " % sno
        res[sno]=calcDirCos(d[0][0].mean(),
                            d[0][1].mean())
    return res

def baselineSolve(s, g, dc,
                  wavel):
    """
    This returns the offsets in the antenna coordinate system

    :param s: Array with scan number of each measurement

    :param g: Array with phase of each measurement

    :param dc: Dictionary of direction cosines

    """
    m=numpy.array([dc[x] for x in s])
    b=numpy.array(g)
    x=numpy.linalg.lstsq(m, b)[0]
    return x*wavel/(2*math.pi)


def baselineExample(msin):
    vtasks.gaincal(msin, 
                   "test.G", 
                   spw="2", 
                   gaintype="G", 
                   calmode="p", 
                   combine="scan")
    dc=scanDirCos(msin)
    wavel=3e8/data.chfspw(msin, 2).mean()
    for a in range(1, data.nant(msin)):
        s, p=getPhases("test.G", a)
        res=baselineSolve(s, p, dc, wavel)
        print "Offset of antenna %i is %s " % (a, str(res))
                          
        
    
    
                     
                     
