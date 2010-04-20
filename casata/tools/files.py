# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
File system tools
"""

import os
import tempfile
import shutil

import casata
from  casata import deco


@deco.casaGlobD
def assembleSPWs(msinl,
                 spwl,
                 msout,
                 data="corrected"):
    r=[]
    for ms, spws in zip(msinl, spwl):
        tms=tempfile.mktemp(suffix=".ms")
        split(vis=ms,
              spw=spws,
              outputvis=tms,
              datacolumn=data)
        r.append(tms)
    concat(vis=r,
           concatvis=msout)
    for tms in r:
        shutil.rmtree(tms)
            