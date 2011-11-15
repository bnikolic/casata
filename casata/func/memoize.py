# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Memoization utilities, for plain Python functions not for fully
funcitonal data analysis
"""

import os
import cPickle

def chName(ms):
    return os.path.splitext(ms)[0]+".pcache"

def openCache(ms):
    if os.access(chName(ms), os.F_OK):
        return cPickle.load(open(chName(ms)))
    else:
        return {}

def saveCache(ms, d):
    cPickle.dump(d, open(chName(ms), "w"))    

def ordKw(kwl):
    return [(k, kwl[k]) for k in kwl.keys()]
    
def MSMemz(f):
    """
    Memoize functions extracting data from measurement set
    """
    def newf(ms, *args, **kwargs):
        c=openCache(ms)
        k=(f.__name__, args, ordKw(kwargs))
        if c.has_key(k):
            return c[k]
        else:
            r=f(*args, **kwargs)
            c[k]=r
            saveCache(ms, c)
            return r
    return newf
    
        
        
