# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for calibration
"""

import os

import casata
from  casata import deco, tools
from casata.tools import  ctools, vtasks, extprog

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


def mkDelaySpW(msin,
               delayl,
               antenna):
    """
    Calibration table for spectral window dependent delay

    :param delayl: List of pairs (spw number, delay value)

    :param antenna: Antenna to apply to
    """
    calname=calTableName(msin, "K", antenna=antenna)
    ctools.gencal(vis=msin,
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
                  precal=[]):
    """
    Calibrate the bandpass on a per-channel basis
    """
    cb=ctools.get("cb")
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
            precal=[],
            spwmap=[]):
    """
    Compute the time-variable antenna-based gain. Incomplete

    """
    calname=calTableName(msin, 
                         "G", 
                         spw=spw)
    ctools.gaincal(vis=msin,
                   caltable=calname,
                   field=calfield,
                   spw=str(spw),
                   selectdata=True,
                   solint="60s",
                   gaintable=precal,
                   combine="",
                   refant="0",
                   minblperant=2,
                   minsnr=-1,
                   solnorm=False,
                   gaintype="G",
                   calmode="ap",
                   spwmap=spwmap)
    return calname
    

def mkGainG(msin,
            calfield,
            spw,
            postf="",
            **kwargs):
    """
    General phase calibration wrapper
    """
    calname=calTableName(msin, 
                         "G"+postf, 
                         spw=spw)    
    vtasks.gaincal(vis=msin,
                   caltable=calname,
                   field=calfield,
                   spw=spw,
                   **kwargs)
    return calname
    
def mkGainBl(msin,
             calfield,
             spw,
             precal=[],
             spwmap=[]):
    """
    Compute the baseline-dependent gain calibration 
    """
    calname=calTableName(msin, 
                         "BL", 
                         spw=spw)    
    vtasks.blcal(vis=msin,
                 caltable=calname,
                 field=calfield,
                 spw=str(spw),
                 solint="inf",
                 gaintable=precal,
                 spwmap=spwmap,
                 gaincurve=False,)
    return calname
    
def wvrgcal(msin,
            wvrflag=[],
            cmdline="wvrgcal"):
    """
    Compute the wvr based calibration
    """
    calname=calTableName(msin, 
                         "W")
    extprog.wvrgcal(msin,
                    calname,
                    wvrflag=wvrflag,
                    cmdline=cmdline)
    return calname
    
