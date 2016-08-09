"""
Closure phase plotting
"""

import textwrap
import numpy
import matplotlib
import matplotlib.pylab as plt
if matplotlib.__version__ > '1.4.0':
     plt.style.use('ggplot')


#import pandas as pd

def twrap(t):
    return "\n".join(textwrap.wrap(t))

def phaseSpec(d, tr=False):
    """Plot closure phases vs frequency on a triad 

    :param d: Phases to plot. If a list then multiple phases are
              over-plotted

    :param tr: Tuple representing the triad. Used to title the plot

    """
    if type(d) == list:
        for x in d:
            plt.plot(x[0,:,0])
    else:
        plt.plot(d[0,:,0])
    plt.ylabel("Closure phase (rad)")    
    plt.xlabel("Channel #")
    if tr:
        plt.title("Closure phase on triad %i-%i-%i" % tuple(tr))

def ampSpec(d, qd=False):
    """Plot closure amplitude vs frequency on a quad
    """
    if type(d) == list:
        for x in d:
            plt.plot(x[0,:,0])
    else:
        plt.plot(d[0,:,0])
    plt.ylabel("Closure amplitude")    
    plt.xlabel("Channel #")
    if qd:
        plt.title("Closure amplitude vs frequency on quad %i-%i-%i-%i" % tuple(qd))


def phaseTime(d):
    for i in range(d.shape[1]):
        plt.plot(d[0,i,:])
    plt.ylabel("Closure phase (rad)")            
    plt.xlabel("Time slot")

def ampTime(d):
    for i in range(d.shape[1]):
        plt.plot(d[0,i,:])
    plt.ylabel("Closure amplitude")            
    plt.xlabel("Time slot")    

def phaseM(d, nside=3):
    plt.figure(dpi=75)
    for t in range(min(len(d["tr"]), nside**2)):
        plt.subplot(nside, nside, t+1)
        #phaseSpec(d["phase"][t])
        phaseTime(d["phase"][t])        
        plt.title("triad-%i-%i-%i" % tuple(d["tr"][t]))

def areaHist(d, bins=30):
    """Plot histogram of areas of triads

    Filters non-finite area values, e.g., due to co-linear baselines
    in a triad

    :param d: Dictionary of values. Value "area" is used. E.g. as
              produced by clquants.triadArea

    """
    d=d["area"]
    m=numpy.isfinite(d)
    plt.hist(d[m], bins=bins)
    plt.xlabel("area in the uv plane (wavelength^2)")
    plt.ylabel("Number of distinct triads")
    plt.title("Histogram of the uv-pane areas of triads")
    
    
             

