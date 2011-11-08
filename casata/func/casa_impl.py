# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Casa implementations of atoms
"""

import files
from atoms import MS

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


