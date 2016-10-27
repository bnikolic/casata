"""
Closure quantities I/O utilities
"""

import casac
import clquants
import numpy
import pandas as pd

def closurePhTriad(msname,
                   triad,
                   fnameout,
                   integ=0,
                   chan={}):
    """

    Closure phase on an a specified triad for one integration.

    Args:

       triad (tuple): The triad to calculate the closure phase for. Order
                      given is respected, i.e., the closure phase is defined in the
                       sense of direction given by the triad.
       fnameout (str): File to writhe the closure phase table to
       integ (int) : Integration to use. Should be Integer value. E.g.,
                     integ=3 means use the third integration in the input measurement
       chan (str): Averaging over frequency channels. See the
                   documentation for split.
    """
    x=clquants.closurePhTriads(msname, [triad], chan=chan)
    nchn=x.shape[2]
    x=pd.DataFrame( { 'Chn#' : numpy.arange(nchn),
                      'Ph'   : x[0,0,:,integ] })
    x.to_csv(fnameout)
    
def dumpDelays(g,
               fnameout):
    tb=casac.casac.table()
    tb.open(g)
    d={}
    for cname in ['TIME',
                  'FIELD_ID',
                  'SPECTRAL_WINDOW_ID',
                  'ANTENNA1',
                  'ANTENNA2',
                  'INTERVAL',
                  'SCAN_NUMBER',
                  'OBSERVATION_ID']:
        d[cname]=tb.getcol(cname)
    for cname in  ['FPARAM',
                   'PARAMERR',
                   'FLAG',
                   'SNR']:
        d[cname+"X"]=tb.getcol(cname)[0,0]
    pd.DataFrame(d).to_csv(fnameout)


