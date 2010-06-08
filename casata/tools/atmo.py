# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for dealing with the atmosphere
"""

import numpy

import casata
from  casata import deco, tools
from casata.tools import  ctools, vtasks

def simAbsModel(flist,
                c,
                fwidths=None):
    """
    Create a simple model of the atmospheric absorption

    :param flist: Frequencies at which to compute the absorption

    :param c: water vapour column in mm (currently not used!)
    
    :param fwidths: Width of each channel

    :returns:  Array of atmospheric *opacities*

    """
    at=ctools.get("at")
    at.initAtmProfile()
    if fwidths is None:
        fwidths=[1]*len(flist)
    at.initSpectralWindow(len(flist),
                          ctools.casac.Quantity(list(flist), "Hz"),
                          ctools.casac.Quantity(list(fwidths), "Hz"),
                          ctools.casac.Quantity([0]*len(flist), "Hz"))
    dry=numpy.array([at.getDryOpacitySpec(x)['dryOpacity'] for x in range(len(flist))])
    return dry
    
    
    
