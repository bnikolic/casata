# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for handling CASA "tools" (that is I guess what you get for
building layers upon layers!)
"""

import casac

_toolMap= {"im" : "imagerHome",
           }

def get(name):
    """
    Return a guranteed unused CASA tool whose state we can change

    For the time being just create a new one each time, but can re-use
    existing tools if this becomes limiting
    """
    t=casac.homefinder.find_home_by_name(_toolMap[name]).create()
    return t


