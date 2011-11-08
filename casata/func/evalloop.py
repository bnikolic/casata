# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Main evaluation loops
"""

import os

import files, endpoints, atoms, casa_impl

from endpoints import MSCpy
from atoms import atom_p, MS, AntPos, WVR
from casata.tools import vtasks
from casa_impl import *

def pl_eval(l):
    if type(l)==str:
        return l
    elif atom_p(l[0]):
        return atom_eval(l)
    else:
        raise "Unknown function type encountered"

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
    #despatch_cmd(cmd)
    return res

def endp_eval(l):
    fn=globals()[l[0]+"_impl"]
    cmd=fn( *map(pl_eval, l[1:-1]), **l[-1])
    print cmd
    #despatch_cmd(cmd)

def go_reduce():
    while len(endpoints.endp):
        c=endpoints.endp[0]
        endp_eval(c)
        endpoints.endp.pop(0)

# Simple example
# MSCpy(WVR(MS("i/uid___A002_Xb9f5d_X1.ms")), "mytest2.ms")
if 1:
    MSCpy(AntPos(WVR(MS("i/uid___A002_Xb9f5d_X1.ms")),
                 [["DV03", [0, 0, 0]],
                  ["DV05", [0.001, 0 , 0]]] ), 
          "mytest2.ms")

def t1(a, b=3):
    pass
