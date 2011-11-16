# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
# Initial version 2010
# 
# This file is part of casata and is licensed under GPL version 2
"""
Get processed data 
"""

import math, numpy

from casata.tools import ctools, vtasks, calibration, data
from casata.func import memoize


def cvPhase(d):
    """
    Return the phase of the complex array d
    """
    return numpy.arctan2(d.imag, d.real)

def getPhasesAnt(caltable,
                 antno):
    """
    Get phases for each scan in caltable for antenna antno
    """
    s, g=data.cal(caltable, 
                  ["SCAN_NUMBER", "GAIN"], 
                  a1=antno)
    if not s.any():
        s=numpy.arange(1,len(s)+1)
    return s, cvPhase(g[0,0])

@memoize.MSMemz
def getPhases(ms,
              combine="", 
              spw="0",
              gaintabs=[]):
    vtasks.gaincal(ms, 
                   "test.G", 
                   spw=spw, 
                   gaintype="G", 
                   calmode="p", 
                   combine=combine,
                   gaintable=gaintabs)
    res=[]
    for a in range(data.nant(ms)):
        res.append(getPhasesAnt("test.G", a))
    return res
    

def calcDirCos(az, el):
    """
    Calculate the direction cosines
    
    :returns: X (east), Y(north), Z(up)
    """
    #Due to timestamp issues there can be an occasional NaN in the
    #az/el. Since we are just interested in the mean we can filter
    #these outs
    mask=numpy.logical_and(numpy.isfinite(az),
                           numpy.isfinite(el))
    return (numpy.sin(az[mask].mean())*numpy.cos(el[mask].mean()),
            numpy.cos(az[mask].mean())*numpy.cos(el[mask].mean()),
            numpy.sin(el[mask].mean()))

@memoize.MSMemz
def scanDirCos(msin,
               warndrift=1e-2):
    """
    Dictionary of direction cosines of each scan in the observation
    """
    res={}
    for sno in data.scans(msin):
        print sno
        d=data.vis(msin,
                   ["TARGET"], 
                   a1=0, 
                   a2=0, 
                   spw=0, 
                   scan=sno)
        if d[0][0].std() > warndrift or d[0][1].std() > warndrift:
            print "Antennas seem to have moved a lot during scan %i " % sno
        res[sno]=calcDirCos(d[0][0],
                            d[0][1])
    return res

