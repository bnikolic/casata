# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for imaging
"""

import os

import casata
from  casata import deco, tools
from casata.tools import ctools

def imageName(msin,
              field,
              algo="hogbom",
              **kwargs):
    """
    Aut-generated names for images
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    pref+=field
    return pref

@deco.casaGlobD
def simpleClean(msin,
                field,
                **kwargs):
    """
    A simple clean of the input data
    """
    clean(vis=msin,
          imagename=imageName(msin, 
                              field=field,
                              ),
          field=field,
          **kwargs)    


def dirty(msin,
          field,
          spw,
          npix=512,
          cell=1.0
          ):
    """
    Make the dirty image

    :param cell: Cell size in arcseconds 
    """
    im=ctools.get("im")
    im.open(msin)
    im.selectvis(field=field,
                 spw=spw)
    im.defineimage(nx=npix, 
                   ny=npix,
                   cellx="%garcsec"% cell,
                   celly="%garcsec"% cell,
                   phasecenter=0,
                   spw=[1])

    fnameout=imageName(msin, 
                       field=field,
                       algo="dirty")
    im.makeimage(type='corrected',
                 image=fnameout)

    
