# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for imaging
"""

import os

import casata
from  casata import deco, tools
from casata.tools import ctools, vtasks, files

def imageName(msin,
              field,
              algo="hogbom",
              spw=None,
              **kwargs):
    """
    Aut-generated names for images
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    pref+=field
    if spw:
        pref+=(".S"+str(spw))
    return pref


def simpleClean(msin,
                field,
                **kwargs):
    """
    A simple clean of the input data
    """
    imagename=imageName(msin, 
                        field=field,
                        **kwargs)
    files.rmClean(imagename)
    vtasks.clean(vis=msin,
                 imagename=imagename,
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
                   spw=[spw])

    fnameout=imageName(msin, 
                       field=field,
                       algo="dirty")
    im.makeimage(type='corrected',
                 image=fnameout)

    
