# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
# 
# This file is part of casata and is licensed under GPL version 2
"""
Export data about skydips 
"""

import numpy

import casata
from casata.tools import data

def wvrskydip(msin, 
              fnameout):
    nant=data.nant(msin)
    t, (az, el), d=data.vis(msin, ["TIME", "TARGET"], spw=0, a1=0, a2=0)
    res={}
    for i in range(nant):
        dname=data.antname(msin, i)
        d=data.vis(msin, ["DATA"], spw=0, a1=i, a2=i)
        res[dname]=d[0]

    fout=open(fnameout, "w")
    fout.write("Time, Azimuth, Elevation, ")
    for i in range(nant):
        aname=data.antname(msin, i)
        for j in range(4):
            fout.write("%s-ch%i, " % (aname, i) )
    fout.write("\n")    

    for k in range(len(t)):
        fout.write("%g, %g, %g, " % (t[k], az[k], el[k]))
        for i in range(nant):
            aname=data.antname(msin, i)
            for j in range(4):
                fout.write("%g" % res[dname][0,j,k] )
        fout.write("\n")
    fout.close()

                       
    
    
    
