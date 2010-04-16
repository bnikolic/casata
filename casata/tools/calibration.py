# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for calibration
"""

import os

import casata
from  casata import deco

def calTableName(msin,
                 caltype,
                 overwrite=True,
                 **kwargs):
    """
    Create a name for caltables
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    res=pref+caltype
    for k in kwargs.keys():
        res=res+"."+k+str(kwargs[k])
    return res

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
    calname=calTableName(msin, "K", antenna=antenna)
    gencal(vis=msin,
           caltable=calname,
           caltype="sbd",
           spw=",".join([str(x[0]) for x in delayl]),
           antenna=str(antenna),
           pol="",
           parameter=[x[1] for x in delayl])
    return calname

def mkBandpassChn(msin,
                  calfield,
                  spw,
                  precal=None):
    """
    Calibrate the bandpass on a per-channel basis
    """
    cb.open(msin)
    cb.selectvis(spw=str(spw),
                 field=calfield)
    calname=calTableName(msin, "B", spw=spw)
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

def mkGainT(msin,
            calfield,
            spw,
            precal=None):
    """
    Compute the time-variable gain. Incomplete
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    calname=pref+".G"
    gaincal(vis=msn,
            caltable=calname,
            field=calfield,
            spw=spw,
            selectdata=True,
            solint="60s",
            gaintable=precal,
            spwmap=[[i],[i]],
            combine="",refant="0",minblperant=2,minsnr=-1,solnorm=False,
            gaintype="G",calmode="ap",
            )
    return calname
    
    

    
