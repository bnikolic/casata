# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for handling CASA "tools" (that is I guess what you get for
building layers upon layers!)
"""

import os

import casac

# Map from usual short names to the "homes"
_toolMap= {"im" : "imagerHome",
           "cb" : "calibraterHome"
           }

def get(name):
    """
    Return a guranteed unused CASA tool whose state we can change

    For the time being just create a new one each time, but can re-use
    existing tools if this becomes limiting
    """
    t=casac.homefinder.find_home_by_name(_toolMap[name]).create()
    return t

def isMS(msin):
    """
    Check if a measurement set exists
    """
    if not os.access(msin, 
                     os.F_OK):
        raise "Could not find measurement set"+msin

# Map from parameter names to their descriptions and functions to
# verify them
_stdParVer={"vis": ("Visibility set (=measurement set?) to operate on",
                    [isMS, ])}

def addPosArgs(args, expect,
               kwargs):
    """
    Add positinoal arguments to the keyworded dictionary
    """
    if len(args) > len(expect):
        raise "Too many positional arguments, was expecting " + str(expect)
    for a, e in zip(args, expect):
        if e in kwargs.keys():
            raise "Positional argument clashes with keyword"
        else:
            kwargs[e]=a

def checkArgs(kwargs):
    """
    Check arguments with standard names using their checker functions
    """
    for k in kwargs:
        if k in _stdParVer.keys():
            doc, cl=_stdParVer[k]
            for c in cl:
                c(kwargs[k])
    

def gencal(*args,
            **kwargs):
    """
    (a replacement for the gencal task)
    """
    addPosArgs(args, 
               ["vis", "caltable"],
               kwargs)
    checkArgs(kwargs)
    cb=get("cb")
    cb.open(kwargs["vis"])
    kwargs.pop("vis")
    cb.specifycal(**kwargs)    
    cb.close()
    
        
