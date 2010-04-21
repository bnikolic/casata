# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Utilities for dealing with time in casa
"""

from casata.tools import ctools


def timeStr(t):
    """
    Convert numerical time as recorded in the measurement set to
    string that can be used for selection

    If the parameter is iterable, all of its component are converted
    """
    qa=ctools.get("qa")
    tu=qa.quantity()
    tu["unit"]="s"
    if hasattr(t, "__iter__"):
        res=[]
        for x in t:
            tu["value"]=x
            res.append(qa.time(tu,
                               form=["ymd"]))
    else:
        tu["value"]=t
        res=qa.time(tu,
                    form=["ymd"])
    return res


def mainStrTimes(msname,
                 rows):
    """
    Return string times coresponding to rows in main table
    """
    tb=ctools.get("tb")
    tb.open(msname)
    times=tb.getcol("TIME")[rows]
    tb.close()
    return timeStr(times)
