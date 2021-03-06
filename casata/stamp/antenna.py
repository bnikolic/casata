# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Quick plots of antenna - related  quantities
"""
import  os

import pylab

import casata
from casata.tools import data,  vtasks




def pos(msin):
    """
    Plot antenna positions
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    fnameout=pref+"-antenna-positions.png"
    # Should do myself in pylab really, since this doesn't work in a
    # headless session
    vtasks.plotants(msin, fnameout)
    return fnameout
