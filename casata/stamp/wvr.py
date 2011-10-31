# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Quick plots of WVR data and related quantities, for quality assurance, etc
"""

import numpy
import pylab

import casata
from casata.tools import data
import utils

def WVRSPW(msin):
    """Return the SPW of the WVR

    Will need to change once SPWs are properly encoded
    """
    for spw in range(data.nspw(msin)):
        f=data.chfspw(msin, spw)
        if len(f) < 5:
            return spw
    

def plot(msin, dotime=True, ch=[0,1,2,3],
         **selkw):
    """
    Plot WVR data
    """
    t, d=data.vis(msin, ["TIME", "DATA"], spw=WVRSPW(msin), **selkw)
    pylab.clf()
    if dotime:
        t=t-t[0]
    else:
        t=numpy.arange(0, 
                       len(t))
    for i in range(d.shape[0]):
        for j in ch:
            pylab.scatter(t, d[i,j].real, s=2)
    fnameout="o/wvr-%s.png" % utils.dataselname(msin, **selkw)
    pylab.savefig(fnameout)
    return fnameout

    
    
    
