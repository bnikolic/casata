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
              fpref=None,
              **kwargs):
    """
    Aut-generated names for images
    """
    pref,junk=os.path.splitext(os.path.basename(msin))
    pref+=("."+field)
    if spw:
        pref+=(".S"+str(spw))
    if algo in ["dirty"]:
        pref+=("."+algo)
    if fpref != None:
        pref=os.path.join(fpref, pref)
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
          cell=1.0,
          **kwargs
          ):
    """
    Make the dirty image

    :param cell: Cell size in arcseconds 
    """
    im=ctools.get("im")
    im.open(msin)
    im.selectvis(field=field,
                 spw=spw,
                 usescratch=True)
    im.defineimage(nx=npix, 
                   ny=npix,
                   cellx="%garcsec"% cell,
                   celly="%garcsec"% cell,
                   phasecenter=int(field),
                   spw=[spw])

    fnameout=imageName(msin, 
                       field=field,
                       spw=spw,
                       algo="dirty",
                       **kwargs)
    im.makeimage(type='corrected',
                 image=fnameout)
    return fnameout

def cleanTest(msin,
              field,
              spw="",
              npix=512,
              cell=1.0,
              niter=1000,
              threshold=0.0,
              weight="uniform",
              gain=0.1,
              boxmask=None,
              centmask=None,
              mask="",
              **kwargs
              ):
    """
    A test of rework of the clean algorithm
    
    :centmask: The clean mask should be the central region of
    diameter/side length of centmax pixels

    """
    imagename=imageName(msin, 
                        field=field,
                        spw=spw,
                        **kwargs)
    im=ctools.get("im")
    qa=ctools.get("qa")
    files.rmClean(imagename)
    im.selectvis(vis=msin,
                 spw=spw,
                 field=field,
                 usescratch=True)
    im.defineimage(nx=npix, 
                   cellx='%g arcsec'% cell,
                   celly='%g arcsec'% cell,
                   spw=spw,
                   phasecenter=int(field))
    im.weight(weight)
    if centmask:
        boxmask=[[npix/2-centmask/2, npix/2-centmask/2],
                 [npix/2+centmask/2, npix/2+centmask/2]]
    if boxmask:
        mask=imagename+".boxmask"
        im.boxmask(mask,
                   boxmask[0],
                   boxmask[1])

    im.clean(algorithm="hogbom", 
             model=imagename+".model", 
             residual=imagename+".residual",
             image=imagename+".image", 
             niter=niter,
             psfimage=imagename+".psf",
             threshold=qa.quantity(threshold,'mJy'),
             gain=gain,
             mask=mask)

    im.done()
    return [imagename+".image", 
            imagename+".model", 
            imagename+".residual",
            imagename+".psf",]

    

    
