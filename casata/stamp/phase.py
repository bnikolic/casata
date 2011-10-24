# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Quick plots of phases
"""
import  os
import numpy

import pylab

import casata
from casata.tools import data,  vtasks, unwrap

import utils

def getp(msin, 
         spw,
         a1, a2,
         field=None,
         scan=None,
         pol=0,
         dounwrap=True):
    """
    Get phase for original and corrected visibilities
    """
    t, d, dc=data.vis(msin, 
                      ["TIME", "DATA", "CORRECTED_DATA"], 
                      spw=spw, 
                      a1=a1, 
                      a2=a2,
                      field=field,
                      scan=scan)
    phu=numpy.degrees(numpy.arctan2(d[pol,0].imag, d[pol,0].real))
    phc=numpy.degrees(numpy.arctan2(dc[pol,0].imag, dc[pol,0].real))
    if dounwrap:
        phu=unwrap.phase(phu, 180)
        phc=unwrap.phase(phc, 180)
    return t, phu, phc
    
def single(msin, 
           spw,
           a1, a2,
           field=None,
           scan=None,
           pol=0,
           dotime=True):
    t, phu, phc=getp(msin, spw, a1, a2, field=field, pol=pol,
                     scan=scan, unwrap=False)
    pylab.clf()
    if dotime:
        t=t-t[0]
    else:
        t=numpy.arange(0, len(t))
    pylab.scatter(t, phu, color="b", s=10)
    pylab.scatter(t, phc, color="r", s=8) 
    fnameout="o/phase-simple-%s.png" % utils.dataselname(msin, spw=spw, a1=a1, 
                                                         a2=a2, field=field,
                                                         scan=scan)
    pylab.savefig(fnameout)
    return fnameout
