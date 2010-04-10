# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for dealing with pointing information in CASA
"""
import scipy
import scipy.interpolate

def offsetAzEl(msin,
               tab=None):
    """
    Return offset pointing interpolated onto the time base of another
    table
    
    :param msin: Input measurement set

    :param tab: Table to interpolate the pointing table times to. If
    none given, will use the main table

    """
    tb.open(msin)
    if tab is None:
        maintime=tb.getcol("TIME")
    else:
        maintime=tab.getcol("TIME")
    tb.open(msin+"/POINTING")
    pointtime=tb.getcol("TIME")
    point=tb.getcol("POINTING_OFFSET")
    ipltor=scipy.interpolate.interp1d(pointtime, 
                                      point[0,0],
                                      kind="linear",
                                      bounds_error=False)
    az=ipltor(maintime)
    ipltor=scipy.interpolate.interp1d(pointtime, 
                                      point[1,0],
                                      kind="linear",
                                      bounds_error=False)
    el=ipltor(maintime)
    tb.close()
    return az, el
