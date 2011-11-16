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
from casata.tools import data, unwrap
from casata.tools.procd import getPhases, scanDirCos

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
    return numpy.radians(unwrap.phase(numpy.degrees(pl), 180))


def blCal(msin, 
          spw="0"):
    dc=scanDirCos(msin)
    wavel=3e8/data.chfspw(msin, int(spw)).mean()
    output_rotated=[0.0,0.0,0.0]
    antenna_list=[str(0)]
    aphases=getPhases(msin,
                      spw=spw)
    rotres={}
    for a in range(1, data.nant(msin)):
        s, p=aphases[a]
        res=baselineSolve(s, 
                          flFirst(p), 
                          dc, 
                          wavel)
        rotres[data.antname(msin, a)]=list(numpy.array(antRotate(res))*-1)
    return rotres
    
def antRotate(res):
    """
    Rotates the antenna position offsets from ENU to the ECEF (Earth
    Centered Earth Fixed) system as used by gencal

    Takes in Antenna offset, length 3, returns list length 3. 
    
    (Sent in by Ed Fomalont)
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

                     
                     
