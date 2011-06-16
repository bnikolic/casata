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


def single(msin, 
           spw,
           a1, a2,
           field=None):
    pref,junk=os.path.splitext(os.path.basename(msin))
    t, d, dc=data.vis(msin, 
                      ["TIME", "DATA", "CORRECTED_DATA"], 
                      spw=spw, 
                      a1=a1, 
                      a2=a2,
                      field=field)
    phu=numpy.degrees(numpy.arctan2(d[0,0].imag, d[0,0].real))
    phc=numpy.degrees(numpy.arctan2(dc[0,0].imag, dc[0,0].real))
    pylab.clf()
    t=t-t[0]
    pylab.scatter(t, phu)
    pylab.scatter(t, phc) 
    fnameout="o/phase-simple-%s-%s-%s.png" % (pref, a1, a2)
    pylab.savefig(fnameout)
    return fnameout
