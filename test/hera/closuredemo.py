
# (setq python-shell-interpreter "/data/p/casa-release-4.7.2-el7/bin/python")
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt


sys.path=["/home/bnikolic/n/casata/clplot/"]+sys.path
import casac
import casa



import bnsimobserve

from clplot import clquants, clplot

def mkcomps():
    cl=casac.casac.componentlist()    
    cl.addcomponent(flux=1.0,
                    fluxunit='Jy',
                    shape='point',
                    dir='J2000 0h0m0 +25d0m0s',
                    freq="1.4 GHz",
                    spectrumtype="Constant")
    cl.addcomponent(flux=1.0,
                    fluxunit='Jy',
                    shape='point',
                    dir='J2000 0h0m0 +25d10m0s',
                    freq="1.4 GHz",
                    spectrumtype="Constant")    

    cl.rename("test5.cl")
    cl.close()

def sim():
    bnsimobserve.simobserve(project="t14",
                            complist="test5.cl",
                            compwidth="1MHz",           
                            mapsize="60 arcsec",
                            antennalist=os.getenv("CASAPATH").split()[0]+"/data/alma/simmos/vla.d.cfg",
                            obsmode="int",
                            integration="100s",
                            setpointings=True,
                            pointingspacing=[],
                            maptype="hex",
                            graphics="file")

    

if 1:
    x=clquants.closurePh("/home/bnikolic/n/casata/test/hera/t14/t14.vla.d.ms", range(10))

plt.figure()
clplot.phaseTime(x["phase"][:,0,:,:])
plt.savefig("test.png")

plt.figure()
plt.matshow(x["phase"][:,0,0,:])
plt.savefig("test2.png")

a=clquants.triadArea("/fast/temp/herareduction/zen.2457545.48011.xx.HH.ms")

if 1:
    x=clquants.closurePh("/fast/temp/herareduction/zen.2457545.48011.xx.HH.ms")

y=clquants.closurePhTriads("/fast/temp/herareduction/zen.2457545.48011.xx.HH.ms",
                           a["tr"][numpy.logical_and (a['area'] > 0,  a['area'] < 1)],
                           chan={"nchan":1, "start": 100, "width": 100, "inc": 100})

    
f=plt.figure(figsize=((20,10)))
ax=f.add_subplot(111)
cax=ax.matshow(y[:,0,0,:])
f.colorbar(cax)
ax.set_yticklabels([''] + [str (zz) for zz in a["tr"][numpy.logical_and (a['area'] > 0,  a['area'] < 1)] ])
ax.set_xlabel("Integration number")
ax.set_yticks(numpy.arange(y[:,0,0,:].shape[0])-1)
ax.set_title("Closure Phase as function of time")
plt.savefig("test4.png")
