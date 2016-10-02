"""
Closure quantities I/O utilities
"""

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

    :param triad: The triad to calculate the closure phase for. Order
    given is respected, i.e., the closure phase is defined in the
    sense of direction given by the triad.

    :param fnameout: File to writhe the closure phase table to

    :param integ: Integration to use. Should be Integer value. E.g.,
    integ=3 means use the third integration in the input measurement

    :param chan: Averaging over frequency channels. See the
    documentation for split.

    """
    x=clquants.closurePhTriads(msname, [triad], chan=chan)
    nchn=x.shape[2]
    x=pd.DataFrame( { 'Chn#' : numpy.arange(nchn),
                      'Ph'   : x[0,0,:,integ] })
    x.to_csv(fnameout)
    


