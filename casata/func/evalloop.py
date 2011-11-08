# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Main evaluation loops
"""

import os

import files, endpoints

from atoms import atom_p, MS
from casata.tools import vtasks
from casa_impl import *

def pl_eval(l):
    if type(l)==str:
        return l
    if atom_p(l[0]):
        return atom_eval(l)

def despatch_cmd(l):
    for c, p in l:
        if c=="sh":
            os.system(p)
        elif c=="vtask":
            #fn=getattr(vtasks, "applycal")
            exec("vtasks."+p)
            
def atom_eval(l):
    if files.cached_p(l):
        return files.cached_res(l)
    fn=globals()[l[0]+"_impl"]
    cmd, res=fn(*l[1:-1], **l[-1])
    files.cache.append([l, res])
    print cmd, res
    despatch_cmd(cmd)
    return res

def endp_eval(l):
    fn=globals()[l[0]+"_impl"]
    cmd=fn( *map(pl_eval, l[1:-1]), **l[-1])
    print cmd
    despatch_cmd(cmd)

def go_reduce():
    while len(endp):
        c=endpoints.endp.pop(0)
        endp_eval(c)

# Simple example
# MSCpy(WVR(MS("i/uid___A002_Xb9f5d_X1.ms")), "mytest2.ms")

