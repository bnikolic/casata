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
from casata.func import memoize

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
                  ["SCAN_NUMBER", "GAIN"], 
                  a1=antno)
    if not s.any():
        s=numpy.arange(1,len(s)+1)
    return s, cvPhase(g[0,0])

@memoize.MSMemz
def getPhasesAll(ms,
                 combine="", 
                 spw="0"):
    vtasks.gaincal(ms, 
                   "test.G", 
                   spw=spw, 
                   gaintype="G", 
                   calmode="p", 
                   combine=combine)
    res=[]
    for a in range(data.nant(ms)):
        res.append(getPhases("test.G", a))
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
    #tb=ctools.get("tb")
    #tb.open(msin)
    
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
    x=numpy.linalg.lstsq(m, b)
    cc=wavel/(2*math.pi)
    return x[0]*cc

def flFirst(p):
    "Filter the phases simply by removing from others the first value"
    return rewrap(p-p[0])

def rewrap(pl):
    res=[]
    for p in pl:
        if p> math.pi:
            res.append(p-2*math.pi)
        elif p < -math.pi:
            res.append(p+2*math.pi)
        else:
            res.append(p)
    return res
    


def baselineExample(msin, 
                    spw="0"):
    dc=scanDirCos(msin)
    wavel=3e8/data.chfspw(msin, int(spw)).mean()
    output_rotated=[0.0,0.0,0.0]
    antenna_list=[str(0)]
    aphases=getPhasesAll(msin,
                         spw=spw)
    rotres={}
    for a in range(1, data.nant(msin)):
        s, p=aphases[a]
        res=baselineSolve(s, 
                          flFirst(p), 
                          dc, 
                          wavel)
        rotres[data.antname(msin, a)]=antRotate(res)
    return rotres
    
def antRotate(res):
    """
    This rotates the antenna solutions from the ENU (east-north) system
    
    to the ECEF (Earth Centered Earth Fixed) system.

    Takes in Antenna offset, length 3, returns list length 3

    Although possibly could be an array of arrays?


    """
    rotateres = []

    #latitude and longitude of ALMA
    latitude = -23.01928333 * 3.14159/180.0
    longitude = 67.75317778 * 3.14159/180.0

    #sin and cos's of ALMA position
    slat = numpy.sin(latitude)
    clat = numpy.cos(latitude)
    slong = numpy.sin(longitude)
    clong = numpy.cos(longitude)

    #Conversion to ECEF coordinate frame
    return [ -res[0]*slong + res[1]*slat*clong - res[2]*clat*clong,
              -res[0]*clong - res[1]*slat*slong - res[2]*clat*slong,
              -res[1]*clat       - res[2]*slat ]

                     
                     
