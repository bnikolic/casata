# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for dealing with pointing information in CASA
"""
import scipy
import scipy.interpolate

import casata
from  casata import deco, tools
from casata.tools import ctools, vtasks, files

def offsetAzEl(msin,
               **kwargs):
    """
    Return pointing offset
    """
    return genPoint(msin,
                    "POINTING_OFFSET",
                    **kwargs)

def genPoint(msin,
             col,
             tab=None,
             a=0):
    """
    Return pointing table column interpolated onto the time base of
    another table
    
    :param msin: Input measurement set

    :param tab: Table to interpolate the pointing table times to. If
    none given, will use the main table

    :param a: Antenna number to get the pointing offset for

    """
    tb=ctools.get("tb")
    tb.open(msin)
    if tab is None:
        maintime=tb.getcol("TIME")
    else:
        maintime=tab.getcol("TIME")
    tb.open(msin+"/POINTING")
    pointtime=tb.getcol("TIME")
    point=tb.getcol(col)
    av=tb.getcol("ANTENNA_ID")
    mask=(av==a)
    ipltor=scipy.interpolate.interp1d(pointtime[mask], 
                                      point[0,0][mask],
                                      kind="linear",
                                      bounds_error=False)
    az=ipltor(maintime)
    ipltor=scipy.interpolate.interp1d(pointtime[mask], 
                                      point[1,0][mask],
                                      kind="linear",
                                      bounds_error=False)
    el=ipltor(maintime)
    tb.close()
    return az, el
