# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Flagging tools
"""

from casata.tools import time, vtasks

def flagRows(msname,
             rlist):
    """
    Flag rows simply according to their sequence number
    """
    vtasks.flagdata(vis=msname,
                    timerange=time.mainStrTimes(rlist))
    

                
