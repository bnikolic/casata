"""
Closure quantities from visibility data
"""

import casac
import numpy

def rewrap(p):
    """
    Rewrap phase to conventional range. Necessary when, e.g.,
    computing closure phase by adding phases
    """
    return numpy.arctan2(numpy.sin(p), numpy.cos(p))

def triads(a1, a2, alist):
    """
    List of all triads in alist
    """
    if len(alist) < 3:
        raise "Need at least three antennas to generate triads"
    nant=len(alist)
    rows=[]
    tr=[]
    for ni, i in enumerate(alist[:-2]):
        for nj, j in enumerate(alist[ni+1:-1]):
            for nk, k in enumerate(alist[ni+nj+2:]):
                p1=numpy.logical_and(a1==i, a2==j).nonzero()[0][0]
                p2=numpy.logical_and(a1==i, a2==k).nonzero()[0][0]
                p3=numpy.logical_and(a1==j, a2==k).nonzero()[0][0]
                rows.append( (p1, p2, p3) )
                tr.append((i,j,k))
    return rows, tr


def closurePh(msname,
              alist,
              chan={},
              signs=[1, -1 , 1]):
    """
    The closure phase on a triad of antennas

    :param alist: The three antennas to compute the closure 

    :param chan: channel averaging (see ms.selectchannel)
    
    :param signs: The signs with which to combine the phases

    """
    ms=casac.casac.ms()
    ms.open(msname)
    ms.select({'antenna1': alist,
               'antenna2': alist })
    if chan: ms.selectchannel(**chan)
    dd=ms.getdata(["antenna1", "antenna2", "phase"], ifraxis=True)
    ph=dd["phase"]
    nant=len(alist)
    rows, tr=triads(dd["antenna1"],
                    dd["antenna2"], alist)
    clp=[]
    for p1,p2,p3 in rows:
        clp.append(rewrap(ph[:,:,p1,:]*signs[0]+ph[:,:,p2,:]*signs[1]+ph[:,:,p3,:]*signs[2]))
    return {"phase": numpy.array(clp),
            "tr": numpy.array(tr)}

def closureAmp(msname,
               alist,
               chan={}):
    """The closure amplitude on a quad of antennas 

    Computes V12 * V34 / (V13 * V24) [see Pearson & Readhead 1984]

    :param alist: The antennas to compute the closure on

    :param chan: channel averaging (see ms.selectchannel)

    """
    if len(alist) < 4:
        raise "Need four antennas for closure amplitude"
    ms=casac.casac.ms()
    ms.open(msname)
    ms.select({'antenna1': alist,
               'antenna2': alist })
    if chan: ms.selectchannel(**chan)
    dd=ms.getdata(["antenna1",  "antenna2", "amplitude"], ifraxis=True)
    aa=dd["amplitude"]
    a1=dd["antenna1"]
    a2=dd["antenna2"]    
    nant=len(alist)
    cla=[]
    tr=[]
    for ni, i in enumerate(alist[:-3]):
        for nj, j in enumerate(alist[ni+1:-2]):
            for nk, k in enumerate(alist[ni+nj+2:-1]):
                for l in alist[ni+nj+nk+3:]:
                    a12=numpy.logical_and(a1==i, a2==j).nonzero()[0][0]
                    a34=numpy.logical_and(a1==k, a2==l).nonzero()[0][0]
                    a13=numpy.logical_and(a1==i, a2==k).nonzero()[0][0]
                    a24=numpy.logical_and(a1==j, a2==l).nonzero()[0][0]                                
                    cla.append( aa[:,:,a12,:] * aa[:,:,a34,:] / (aa[:,:,a13,:] * aa[:,:,a24,:] ))
                    tr.append((i,j,k,l))    
    return {"amp": numpy.array(cla), # The closure amplitude
            "quad": numpy.array(tr)} # Quad on which it was computed
            

