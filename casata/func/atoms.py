# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Indivisible operations on measurement sets and cal tables
"""

import macro 

def AtomMS(f):
    """
    Define an indivisible operation on the measurement set
    """
    rf=macro.Macro(f)
    rf.expand=None
    return rf

@AtomMS
def WVR(ms):
    """
    Correct the phases of visibilities based on WVR data
    """
    return None
