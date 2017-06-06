# (setq python-shell-interpreter "/data/p/casa-release-4.7.2-el7/bin/python")

import casac
import casa

import bnsimobserve

def mkcomps():
    cl=casac.casac.componentlist()    
    cl.addcomponent(flux=1.0,
                    fluxunit='Jy',
                    shape='point',
                    dir='J2000 0h0m0 +25d0m0s',
                    freq="1.4 GHz",
                    spectrumtype="Constant")

    cl.rename("test4.cl")
    cl.close()

def sim():
    bnsimobserve.simobserve(project="t12",
                            complist="test4.cl",
                            compwidth="1MHz",           
                            mapsize="60 arcsec",
                            antennalist=os.getenv("CASAPATH").split()[0]+"/data/alma/simmos/vla.d.cfg",
                            obsmode="int",
                            integration="1s",
                            setpointings=True,
                            pointingspacing=[],
                            maptype="hex",
                            graphics="file")



