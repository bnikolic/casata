# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for handling CASA "tools" (that is I guess what you get for
building layers upon layers!)
"""

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

# Map from parameter names to their descriptions and functions to
# verify them
_stdParVer={"vis": ("Visibility set (=measurement set?) to operate on",
                    [])}

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
    

def gencal(*args,
            **kwargs):
    """
    (a replacement for the gencal task)
    """
    addPosArgs(args, 
               ["vis", "caltable"],
               kwargs)
    cb=get("cb")
    cb.open(kwargs["vis"])
    kwargs.pop("vis")
    cb.specifycal(**kwargs)    
    cb.close()
    
        
