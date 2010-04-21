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
from casata.tools import vtasks


def assembleSPWs(msinl,
                 spwl,
                 msout,
                 data="corrected"):
    r=[]
    for ms, spws in zip(msinl, spwl):
        tms=tempfile.mktemp(suffix=".ms")
        # Looks like split has a "hidden" 13th parameter? Wonder how
        # that works?
        vtasks.split(ms,
                     tms,
                     data,
                     "",
                     spws,
                     "",
                     "",
                     "",
                     "",
                     "",
                     "",
                     "",
                     "")
        r.append(tms)
    vtasks.concat(r,
                  msout,
                  "",
                  "",
                  False)
    for tms in r:
        shutil.rmtree(tms)
            
