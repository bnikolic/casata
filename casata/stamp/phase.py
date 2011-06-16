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
from casata.tools import data,  vtasks

import utils

def single(msin, 
           spw,
           a1, a2,
           field=None,
           dotime=True):
    t, d, dc=data.vis(msin, 
                      ["TIME", "DATA", "CORRECTED_DATA"], 
                      spw=spw, 
                      a1=a1, 
                      a2=a2,
                      field=field)
    phu=numpy.degrees(numpy.arctan2(d[0,0].imag, d[0,0].real))
    phc=numpy.degrees(numpy.arctan2(dc[0,0].imag, dc[0,0].real))
    pylab.clf()
    if dotime:
        t=t-t[0]
    else:
        t=numpy.arange(0, len(t))
    pylab.scatter(t, phu, color="b", s=10)
    pylab.scatter(t, phc, color="r", s=8) 
    fnameout="o/phase-simple-%s.png" % utils.dataselname(msin, spw=spw, a1=a1, 
                                                         a2=a2, field=field)
    pylab.savefig(fnameout)
    return fnameout
