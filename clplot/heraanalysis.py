import numpy
import pandas as pd
import clplot.clquants as clquants

def mapd(f, d):
    "map over dictionary values"
    return dict( [ (k,f(v)) for k,v in d.iteritems() ])

def comparableAmps(dd, qd,
                   fout):
    "CSV output of values"
    p=mapd(lambda msin: clquants.closureAmp(msin, alist=qd),
           dd)
    # Get the frequency axis only
    p=mapd(lambda a: a['amp'][0,0,:,0],
           p)
    chno=numpy.arange(p[p.keys()[0]].shape[0])
    df=pd.DataFrame(p, index=chno)
    df.to_csv(fout)
    
