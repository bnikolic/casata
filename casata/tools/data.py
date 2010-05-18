# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for extracting data from MS
"""

import casata
from  casata import deco, tools
from casata.tools import ctools

def buildquery(ms,
               **kwargs):
    """
    Build a table select query based on casata convention parameters

    Each kwarg is used according to the standard meaning defined by
    this function
    """
    q=""
    if  kwargs.get("a1") is not None:
        q+=("ANTENNA1==%i &&" % kwargs["a1"])
    if kwargs.get("a2")  is not None:
        q+=("ANTENNA2==%i &&" % kwargs["a2"])
    if kwargs.get("scan")is not None:
        q+=("SCAN_NUMBER==%i &&" % kwargs["scan"])
    if kwargs.get("subscan") is not None:
        q+=sub_scan_q(ms, kwargs["subscan"])
    return q[:-2]

def sub_scan_q(ms,
               ss):
    """
    Figure out the index for subscan id
    """
    tb=ctools.get("tb")
    tb.open(ms+"/STATE")
    s=tb.getcol("SUB_SCAN")
    m=(s==ss).nonzero()
    if len(m) > 1:
        raise "Multiple matches, cant do this yet"
    return ("STATE_ID==%i &&" % m[0][0])
    

def vis(ms,
        cols=[],
        **kwargs):
    """
    Get data from a measurement main table and associated tables

    This function should avoid using helper columns like data_id etc
    and instead parse the auxiliary tables to ease interaction. 

    Also it should offer knows columns that are not part of the main
    table by suitable interpolation

    :param cols: List of columns to get
    """
    tb=ctools.get("tb")
    tb.open(ms)
    tbres=tb.query(buildquery(ms, **kwargs))
    res=[]
    for col in cols:
        res.append(tbres.getcol(col))
    return res
    
    
