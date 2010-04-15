# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for calibration
"""

import os

import casata
from  casata import deco

@deco.casaGlobD
def mkDelaySpW(msin,
               delayl,
               antenna):
    """
    Calibration table for spectral window dependent delay

    :param delayl: List of pairs (spw number, delay value)

    :param antenna: Antenna to apply to
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    calname=pref+".K"
    gencal(vis=msin,
           caltable=calname,
           caltype="sbd",
           spw=",".join([str(x[0]) for x in delayl]),
           antenna=str(antenna),
           pol="",
           parameter=[x[1] for x in delayl])
    return calname
    

    
