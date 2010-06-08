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
                c):
    """
    Create a simple model of the atmospheric absorption

    :param fc: Centre frequency to grid to compute for

    :param c: water vapour column in mm
    """
    at=ctools.get("at")
    at.initAtmProfile()
    at.initSpectralWindow(len(flist),
                          ctools.casac.Quantity(flist, "Hz"),
                          ctools.casac.Quantity([1]*len(flist), "Hz"),
                          ctools.casac.Quantity([0]*len(flist), "Hz"))
    dry=numpy.array([at.getDryOpacitySpec(x)['dryOpacity'] for x in range(len(flist))])
    return dry
    
    
    
