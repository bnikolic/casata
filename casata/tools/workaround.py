# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for working around problems in CASA which are considered fixable
in the (near) future
"""
import os
import tempfile
import shutil

import casata
from  casata import deco

@deco.casaGlobD
def fixPointingFill(msin):
    """
    Fix problems with pointing table in present in some datasets
    filled from the ASDM.

    The current implementation is to export to uvfits and reimport and
    then reuse the pointing table. This workaround is after Martin
    Zwaan's mapN3256B6new.py.txt
    """
    fitsname=tempfile.mktemp(suffix=".fits")
    exportuvfits(vis=msin,
                 fitsfile=fitsname,
                 datacolumn="data",
                 field="",
                 spw="0",
                 antenna="",
                 timerange="",
                 nchan=-1,
                 start=0,
                 width=1,
                 writesyscal=False,
                 multisource=True,
                 combinespw=True,
                 writestation=True)
    msnewname=tempfile.mktemp(suffix=".ms")
    importuvfits(fitsfile=fitsname,
                 vis=msnewname,
                 antnamescheme="old")
    os.remove(fitsname)
    oldpoint=os.path.join(msin,
                          "POINTING")
    newpoint=os.path.join(msnewname,
                          "POINTING")
    shutil.rmtree(oldpoint)
    shutil.copytree(newpoint,
                    oldpoint)
    shutil.rmtree(msnewname)
    
    
    
