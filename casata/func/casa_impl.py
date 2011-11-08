# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Casa implementations of atoms
"""

import numpy


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

def mkGenCalAP(antposl):
    """
    Turn antenna position list into the strange format gencal understands
    """
    anames=",".join([x[0] for x in antposl])
    apos=list(numpy.array([x[1] for x in antposl]).flatten())
    return anames, apos
    

def AntPos_impl(msin, 
                antposl, 
                *args, **kwargs):
    msin=MSName(msin)
    # Sort, so that simply re-ordering the antennas does not cause a
    # cache miss
    antposl.sort()
    msout=files.new_ms(["AntPos", msin, antposl] + list(args) + [kwargs])
    anames, apos=mkGenCalAP(antposl)
    return [ ["vtasks", "gencal('%s', caltable='%s', caltype='antpos', antenna='%s', parameter=%s" % (msin,
                                                                                                      "temp.APos",
                                                                                                      anames,
                                                                                                      apos)],
             ["vtask", "applycal('%s', gaintable=[\"temp.APos\"])" % msin],
             ["vtask", "split('%s', outputvis='%s', datacolumn='corrected')" % (msin, msout)]
             ], MS(msout)



