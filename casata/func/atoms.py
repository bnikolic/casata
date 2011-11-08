# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Indivisible operations on measurement sets and cal tables
"""

import os

import macro, files
 
_atoml=[]

def atom_p(n):
    return n in _atoml

def AtomMS(f):
    """
    Define an indivisible operation on the measurement set
    """
    rf=macro.Macro(f)
    rf.expand=None
    _atoml.append(f.func_name)
    return rf

@AtomMS
def MS(fnamein):
    """
    """
    return None

@AtomMS
def WVR(ms):
    """
    Correct the phases of visibilities based on WVR data
    """
    return None






