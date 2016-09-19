# (setq python-shell-interpreter "/data/p/casa-release-4.6.0-el6/bin/python")

import sys
sys.path.append("../../clplot/")

from matplotlib import pylab
from clplot import clquants
msavg='/fast/temp/casaclosure2/CygA-timeavg.ms'

trset=[[53, 104, 80],  [22, 9, 20]]
xx=clquants.phTriads(msavg, trset)

timeint=-2

f, axarr = pylab.subplots(3, sharex=True)
i=1
axarr[0].plot(clquants.rewrap(xx[i][0][0][0,:,timeint]*xx[i][1][0] + xx[i][0][1][0,:,timeint]*xx[i][1][1] + xx[i][0][2][0,:,timeint]*xx[i][1][2]), label=("triad %i-%i-%i"%tuple(trset[i])))
axarr[0].plot(clquants.rewrap(xx[0][0][0][0,:,timeint]*1.0 + xx[0][0][1][0,:,timeint]*-1.0 + xx[0][0][2][0,:,timeint]*-1.0), label=("manual triad %i-%i-%i"%tuple(trset[0])))        
axarr[0].set_title('d')
axarr[0].legend()
for i in range(3):
    axarr[1].plot(xx[0][0][i][0,:,timeint], label="trace %i " % i)
axarr[1].legend()
for i in range(3):
    axarr[2].plot(xx[1][0][i][0,:,timeint], label="trace %i " % i)
axarr[2].legend()
pylab.show()
