"""
Closure quantities from visibility data
"""

import casac
import numpy

def rewrap(p):
    """
    Rewrap phase so that branch cut is along the negative real axis.
    """
    return numpy.arctan2(numpy.sin(p), numpy.cos(p))

def eitherWay(a1, a2, i, j):
    """Return rows where a1==i and a2==j OR a1==j and a2==i. Also return
    sign +1 if former or -1 if latter.

    """
    r1=numpy.logical_and(a1==i, a2==j).nonzero()[0]
    if r1.shape[0]:
        return r1[0], +1.0
    else:
        return numpy.logical_and(a1==j, a2==i).nonzero()[0][0], -1.0

def triadRows(a1, a2, tr):
    """
    Rows corresponding to single triad tr
    """
    i,j,k=tr
    p1,s1=eitherWay(a1, a2, i, j)
    p2,s2=eitherWay(a1, a2, j, k)
    p3,s3=eitherWay(a1, a2, k, i)
    return ( (p1, p2, p3),
             (s1, s2, s3))

def quadRows(a1, a2, qd):
    """
    Rows corresponding to a single quad qd
    """
    i,j,k,l=qd
    a12,s1=eitherWay(a1, a2, i, j)
    a34,s2=eitherWay(a1, a2, k, l)
    a13,s3=eitherWay(a1, a2, i, k)
    a24,s4=eitherWay(a1, a2, j, l)
    return (a12, a34, a13, a24)
    


def triads(a1, a2, alist):
    """
    List the rows corresponding to all triads in alist
    
    :param a1, a2: Arrays with antenna IDs for first and second antenna
    :param alist:  List of antenna IDs for which to generate the triads

    :returns: Tuple of (list of (tuple containing rows with data in the triad)), 
              (list of tuples contianing antenna IDs in the triad),
              (list of signs to be used in computing a closure phase)

    """
    if len(alist) < 3:
        raise "Need at least three antennas to generate triads"
    nant=len(alist)
    rows=[]
    tr=[]
    signs=[]
    for ni, i in enumerate(alist[:-2]):
        for nj, j in enumerate(alist[ni+1:-1]):
            for nk, k in enumerate(alist[ni+nj+2:]):
                ( (p1, p2, p3),
                  (s1, s2, s3)) = triadRows(a1, a2, (i,j,k))
                rows.append( (p1, p2, p3) )
                tr.append((i,j,k))
                signs.append( (s1, s2, s3))
    return rows, tr, signs


def closurePh(msname,
              alist,
              chan={}):
    """
    The closure phase on a triad of antennas

    :param alist: The three antennas to compute the closure 

    :param chan: channel averaging (see ms.selectchannel)

    :returns: Dictionary with an array containing phases and an array with the triad ids

    """
    ms=casac.casac.ms()
    ms.open(msname)
    ms.select({'antenna1': alist,
               'antenna2': alist })
    if chan: ms.selectchannel(**chan)
    # Note the use of ifraxis. This means time and interfoerometer
    # number are separate dimensions in the returned data
    dd=ms.getdata(["antenna1", "antenna2", "phase"], ifraxis=True)
    ms.close()
    ph=dd["phase"]
    rows, tr, signs=triads(dd["antenna1"],
                           dd["antenna2"], alist)
    clp=[]
    for (p1,p2,p3), (s1,s2,s3) in zip(rows,signs):
        clp.append(rewrap(ph[:,:,p1,:]*s1+ph[:,:,p2,:]*s2+ph[:,:,p3,:]*s3))
    return {"phase": numpy.array(clp),
            "tr": numpy.array(tr)}

def phTriads(msname,
             triadlist,
             chan={}):
    """
    Phase on all baselines in a triad

    """
    ms=casac.casac.ms()
    ms.open(msname)
    if chan: ms.selectchannel(**chan)
    # Note the use of ifraxis. This means time and interfoerometer
    # number are separate dimensions in the returned data
    dd=ms.getdata(["antenna1", "antenna2", "phase"], ifraxis=True)
    ph=dd["phase"]; a1=dd["antenna1"]; a2=dd["antenna2"]
    ms.close()
    res=[]
    for tr in triadlist:
        ( (p1, p2, p3),
          (s1, s2, s3)) = triadRows(a1, a2, tr)
        res.append(  ((ph[:,:,p1,:], ph[:,:,p2,:], ph[:,:,p3,:]),
                      (s1, s2, s3)))
    return res

def phBaseline(msname,
               i, j,
               chan={}):
    """
    Phase on the baseline between antennas i and j
    """
    ms=casac.casac.ms()
    ms.open(msname)
    if chan: ms.selectchannel(**chan)
    # Note the use of ifraxis. This means time and interfoerometer
    # number are separate dimensions in the returned data
    dd=ms.getdata(["antenna1", "antenna2", "phase"], ifraxis=True)
    ph=dd["phase"]; a1=dd["antenna1"]; a2=dd["antenna2"]
    ms.close()
    p1,s1=eitherWay(a1, a2, i, j)
    return (ph[:,:,p1,:], s1)


def closurePhTriads(msname,
                    triadlist,
                    chan={}):
    """Closure phase on specified trads

    Unlike closurePh specific triads are taken and used in the order
    given

    """
    ms=casac.casac.ms()
    ms.open(msname)
    if chan: ms.selectchannel(**chan)
    # Note the use of ifraxis. This means time and interfoerometer
    # number are separate dimensions in the returned data
    dd=ms.getdata(["antenna1", "antenna2", "phase"], ifraxis=True)
    ph=dd["phase"]; a1=dd["antenna1"]; a2=dd["antenna2"]
    ms.close()
    res=[]
    for tr in triadlist:
        ( (p1, p2, p3),
          (s1, s2, s3)) = triadRows(a1, a2, tr)
        phr=rewrap(ph[:,:,p1,:]*s1+ph[:,:,p2,:]*s2+ph[:,:,p3,:]*s3)
        res.append(phr)
    return numpy.array(res)


def triangleArea(u1, v1, u2, v2, u3, v3):
    """
    Area of a triangle calculated from the vectors forming its sides
    """
    l1, l2, l3=map( lambda (x,y): numpy.sqrt(x**2+y**2),
                   [ [u1, v1],
                     [u2, v2],
                     [u3, v3]])
    p=0.5*(l1+l2+l3)
    return numpy.sqrt(p*(p-l1)*(p-l2)*(p-l3))

def triadArea(msname,
              alist=None,
              chan={}):
    """Compute the area in the uv plane of all triads formed by antenna IDs
    alist

    Area is calculated on the projection on the uv plane, so w is ignored

    :param msname: Input measurement set

    :param alist: List of antenna IDs. If none is supplied all
    antennas are considered

    :param chan: Dictionary with channel averaging specification. See
                 the syntax for ms.selectchannel.

    :returns: Dictionary with array of areas and triads that does areas correspond to

    """
    ms=casac.casac.ms()
    ms.open(msname)
    if alist is None:
        aa=ms.getdata(["antenna1", "antenna2"])
        aa=numpy.append(aa["antenna1"],aa["antenna2"])
        alist=numpy.unique(aa)
    ms.select({'antenna1': alist,
               'antenna2': alist })
    if chan: ms.selectchannel(**chan)
    dd=ms.getdata(["antenna1", "antenna2", "u", "v"], ifraxis=True)
    u,v =dd["u"], dd["v"]
    rows, tr, signs=triads(dd["antenna1"],
                           dd["antenna2"], alist)
    clp=[]
    for p1,p2,p3 in rows:
        clp.append(triangleArea(u[p1,:], v[p1,:],
                                u[p2,:], v[p2,:],
                                u[p3,:], v[p3,:]))
    # The area for first itegration only is returned
    return {"area": numpy.array(clp)[:,0],
            "tr": numpy.array(tr)}

def closureAmpQd(msname,
                 qd,
               chan={}):
    """The closure amplitude on a single quad of antennas 

    Computes V12 * V34 / (V13 * V24) [see Pearson & Readhead 1984]

    :param msname: Measurement Set to measure
    :param qd: List with the antenna IDs of the quad
    :param chan: channel averaging (see ms.selectchannel)

    """
    ms=casac.casac.ms()
    ms.open(msname)
    ms.select({'antenna1': qd,
               'antenna2': qd })
    if chan: ms.selectchannel(**chan)
    dd=ms.getdata(["antenna1",  "antenna2", "amplitude"], ifraxis=True)
    aa=dd["amplitude"]
    a1=dd["antenna1"]
    a2=dd["antenna2"]    
    (a12, a34, a13, a24)=quadRows(a1, a2, qd)
    return aa[:,:,a12,:] * aa[:,:,a34,:] / (aa[:,:,a13,:] * aa[:,:,a24,:] )
            



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
            

def reorrder(msname):
    """
    Re-order antenna 1 & 2 in each correlation so 2 is greater than 1
    """
    ms=casac.casac.table()
    ms.open(msname, nomodify=False)
    a1, a2, data = [ms.getcol(x) for x in ["ANTENNA1",  "ANTENNA2", "DATA"] ]
    m=a1 > a2
    data[:,:,m]=data[:,:,m].conj()
    x=a2[m]
    a2[m]=a1[m]
    a1[m]=x
    ms.putcol("ANTENNA1", a1)
    ms.putcol("ANTENNA2", a2)
    ms.putcol("DATA", data)
    ms.flush()
    ms.close()
