# Demo scripts known to run on appcs

import os

import matplotlib.pylab as plt

from clplot import clplot, clquants
from heraanalysis import *

datadir="/appcs/data/bn204/hera/data"

d_fg=os.path.join(datadir, "FOREGROUND.H37.ms")
d_21=os.path.join(datadir, "21cm.H37.ms")
d_comb=os.path.join(datadir, "21CM+FG.H37.ms")

def plotacomp(fl, qd):
    p=map(lambda msin: clquants.closureAmp(msin, alist=qd),
	  fl)
    plt.subplot(211)
    clplot.ampSpec([pp["amp"][0] for pp in p], qd=qd)
    plt.subplot(212)
    clplot.ampSpec(p[2]["amp"][0]- p[0]["amp"][0])
    plt.title(clplot.twrap("quad-%i-%i-%i-%i: Difference between the combined 21+foreground and the foreground-only signal " % tuple(qd) ))
    plt.tight_layout()
    plt.show()
plotacomp([d_fg, d_21, d_comb],  [2,3,4,5])

# Exports the data to CSV
comparableAmps({"21cm" : d_21, "foreground" : d_fg, "combined" : d_comb}, [2,3,4,5], "test.csv")
