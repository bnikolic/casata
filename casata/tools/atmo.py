# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for dealing with the atmosphere
"""

import casata
from  casata import deco, tools
from casata.tools import  ctools, vtasks

def simAbsModel(fc, fw, fr,
                c):
    """
    Create a simple model of the atmospheric absorption

    :param fc: Centre frequency to grid to compute for

    :param c: water vapour column in mm
    """
    at=ctools.get("at")
    at.initAtmProfile()
    at.initSpectralWindow(1, 
                          ctools.casac.Quantity(fc, "Hz"),
                          ctools.casac.Quantity(fw, "Hz"),
                          ctools.casac.Quantity(fr, "Hz"),
                          )
    dry=at.getDryOpacitySpec()
    return dry
    
    
    
