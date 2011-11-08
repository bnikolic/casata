# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Indivisible operations on measurement sets and cal tables
"""

import os

import macro, files
from casa_impl import *
 
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

endp=[]

def EndP(f):
    """
    Defines an end-point of computation, i.e., point where output
    (==sideffect) occurs
    """
    def rf(*pars, **kwargs):
        endp.append([f.func_name] + list(pars) + [kwargs])
    return rf

@EndP
def MSCpy(ms,
          fnameout):
    """
    Copy processed data to output dataset. Use only for interoperation
    with other software
    """
    return None



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
        c=endp.pop(0)
        endp_eval(c)

# Simple example
# MSCpy(WVR(MS("i/uid___A002_Xb9f5d_X1.ms")), "mytest2.ms")




