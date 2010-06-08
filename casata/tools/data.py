# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for extracting data from MS
"""
import numpy

import casata
from  casata import deco, tools
from casata.tools import ctools, pointing

def buildquery(ms,
               **kwargs):
    """
    Build a table select query based on casata convention parameters

    Each kwarg is used according to the standard meaning defined by
    this function
    """
    q=""
    if  kwargs.get("a1") is not None:
        q+=antenna_q(ms,
                     kwargs["a1"],
                     1)
    if kwargs.get("a2")  is not None:
        q+=antenna_q(ms,
                     kwargs["a2"],
                     2)
    if kwargs.get("scan")is not None:
        q+=("SCAN_NUMBER==%i &&" % kwargs["scan"])
    if kwargs.get("subscan") is not None:
        q+=sub_scan_q(ms, kwargs["subscan"])
    if kwargs.get("spw") is not None:
        q+=spw_q(ms, kwargs["spw"])
    if kwargs.get("field") is not None:
        q+=("FIELD_ID==%i &&" % kwargs["field"])
    return q[:-2]

def antenna_q(ms,
              a,
              ano):
    """
    Sub-query on antennas

    :param a: Antenna to select.
    """
    if type(a) is str:
        tb=ctools.get("tb")
        tb.open(ms+"/ANTENNA")
        s=tb.getcol("NAME")
        m=(s==a).nonzero()
        if len(m) > 1:
            raise "Multiple matches, cant do this yet"
        a=m[0][0]
    return ("ANTENNA%i==%i &&" % (ano,
                                  a))
        

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

def spw_q(ms,
          spw):
    """
    Figure out query to select a signle spectral window
    """
    tb=ctools.get("tb")
    tb.open(ms+"/DATA_DESCRIPTION")
    s=tb.getcol("SPECTRAL_WINDOW_ID")
    m=(s==spw).nonzero()
    if len(m) > 1:
        raise "Multiple matches, cant do this yet"
    return ("DATA_DESC_ID==%i &&" % m[0][0])    

# These are the columns that must be fetched from other tables
_speccols=["POINTING_OFFSET"]

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
    maincols=[x for x in cols if x not in _speccols]
    for col in cols:
        if col in maincols:
            res.append(tbres.getcol(col))
        elif col == "POINTING_OFFSET":
            for a in ["a1", "a2"]:
                if kwargs.get(a) is not None:
                    res.append(pointing.offsetAzEl(ms, 
                                                   tbres,
                                                   a=kwargs[a]))
    return res
    

def closurePh(msin,
              alist,
              col="DATA",
              signs=[1, -1 , 1],
              **kwargs):
    """
    The closure phase on a triad of antennas

    :param alist: The three antennas to compute the closure for
    
    :param cal: Data column to use, i.e., "DATA", "CORRECTED_DATA" 

    :param signs: The signs with which to combine the phases
    """
    if len(alist) != 3:
        raise "Need three antennas for closure phase"
    def phase(a1, a2):
        d=vis(msin, 
              [col], 
              a1=a1, 
              a2=a2, 
              **kwargs)[0]
        ph=numpy.degrees(numpy.arctan2(d.imag, 
                                       d.real))
        return ph
    cl=phase(alist[0], alist[1])-phase(alist[0], alist[2])+phase(alist[1], alist[2])
    cl=(cl+180)%360-180
    return cl

def nspw(msin):
    """
    The number of spectral windows in this measurement set
    """
    tb=ctools.get("tb")
    tb.open(msin+"/SPECTRAL_WINDOW")
    return tb.nrows()
    
def chfspw(msin,
         spw):
    """
    Return the frequencies of channels in spw
    """
    tb=ctools.get("tb")
    tb.open(msin+"/SPECTRAL_WINDOW")
    x=tb.getvarcol("CHAN_FREQ")
    return x["r%i"%(spw+1)][:,0]

def chwspw(msin,
           spw):
    """
    Return the widths of channels in spw
    """
    tb=ctools.get("tb")
    tb.open(msin+"/SPECTRAL_WINDOW")
    x=tb.getvarcol("CHAN_WIDTH")
    return x["r%i"%(spw+1)][:,0]
    
