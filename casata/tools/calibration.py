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

def mkBandChn(msin,
              calfield,
              spw,
              precal=None):
    """
    Calibrate the bandpass on a per-channel basis
    """
    cb.open(msin)
    cb.selectvis(spw=str(spw),
                 field=calfield)
    pref,junk=os.path.splitext(os.path.basename(msin))
    calname=pref+".B"
    cb.setsolve(table=calname,    
                type="B",
                t="inf",
                combine="scan",
                minblperant=2,
                solnorm=False,
                minsnr=-2)    
    for  p in precal:
        cb.setapply(table=p,
                    spwmap=[spw])   
    cb.solve()
    cb.close()
    return calname
    
    

    
