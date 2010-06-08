# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Quick plots of atmospheric propeties / effects 
"""
import os

import numpy
import pylab

import casata
from casata.tools import data, atmo

def dryAbs(msin):
    """
    Plot the dry atmospheric absorption for each spw in the
    measurement set with more than one channel
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    for spw in range(data.nspw(msin)):
        f=data.chfspw(msin, spw)
        if len(f) == 1:
            continue
        a=atmo.simAbsModel(f,
                           0,
                           fwidths=data.chwspw(msin, spw))
        pylab.clf()
        pylab.plot(f/1e9, numpy.exp(-a))
        pylab.ylabel("Atmospheric transmission")
        pylab.xlabel("Frequency (GHz)")
        pylab.savefig((pref+"-spw%i-dry-trans.png") % spw)
    
                         
        
        
