# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Indivisible operations on measurement sets and cal tables
"""

import macro, files

def AtomMS(f):
    """
    Define an indivisible operation on the measurement set
    """
    rf=macro.Macro(f)
    rf.expand=None
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
    pass

def atom_eval(l):
    fn=globals()[l[0]+"_impl"]
    cmd, res=fn(*l[1:-1], **l[-1])
    files.cache.append([l, res])
    print cmd, res

def MSName(l):
    if l[0]=="MS":
        return l[1]

def WVR_impl(msin, *args, **kwargs):
    msin=MSName(msin)
    msout=files.new_ms(["WVR", msin] + list(args) + [kwargs])
    return [ ["sh", "/home/bnikolic/n/libair/head/cmdline/wvrgcal --ms %s --output temp.W" % msin],
             ["vtask", "applycal('%s', gaintable=[\"temp.W\"])" % msin],
             ["vtask", "split('%s', outputvis='%s', datacolumn='corrected')" % (msin, msout)]
             ], MS(msout)

def MSCpy_impl(msin, fnameout):
    return [ ["sh", "cp -r %s %s" % (MSName(msin), fnameout) ]]




