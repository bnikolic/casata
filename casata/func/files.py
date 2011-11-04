# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
File and cache managemnt for functional programming data reduction
"""

import os

cache=[]

def cached_p(l):
    return any([x[0]==l for x in cache])

def cached_res(l):
    for x in cache:
        if x[0]==l: 
            return x[1]

def newfname(pref, suf):
    i=0
    fname="cache/%s-%i.%s" % (pref, i, suf)
    while os.access(fname, os.F_OK):
            i=i+1
            fname="cache/%s-%i.%s" % (pref, i, suf)
    return fname

def new_ms(l):
    f=newfname(l[0], "ms")
    return f


