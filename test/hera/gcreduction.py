import os, shutil
# Notes on GC data-reduction

import clplot.clquants as clquants

    
msin="/fast/temp/t/GC.ms"
mspr="/fast/temp/t/GC-pr.ms"

if 1:
    shutil.rmtree(msin, ignore_errors=True); shutil.rmtree(mspr, ignore_errors=True)
    importuvfits("/data/archive/HERA-5/zen.2457545.48707.xx.HH.uvcU.uvfits", msin)
    # This is essential. A routine in clplot.clquants
    clquants.reorrder(msin)

if 0:
    cl.addcomponent(flux=1.0, fluxunit='Jy',shape='point', dir='J2000 17h45m40.0409s -29d0m28.118s', spectrumtype='spectral index', index=-1.0)  
    cl.rename("GC-indx.cl")
    cl.close()

if 1:
    ft(msin, complist="GC.cl", usescratch=True)

if 0:
    ft(msin, complist="GC-indx.cl", usescratch=True)

if 1:
    fixvis(msin, mspr, phasecenter="J2000 17h45m40s -29d00m28s")
    flagdata(mspr, flagbackup=T,        mode='manual', antenna="82")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:0~65")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:377~387")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:850~854")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:930~1024")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:831")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:769")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:511")
    flagdata(mspr, flagbackup=T,        mode='manual', spw="0:913")                
    flagdata(mspr, autocorr=True)    

if 0:
    gaincal(mspr, caltable="g18", gaintype='G', solint='inf',  refant="43", spw='0:400~600', minsnr=2, calmode='ap', gaintable="g16")
    applycal(mspr, gaintable=["g16", "g18"])
    clean(mspr, "test3", niter=1000, mode="mfs", nterms=1, imsize=[400,400], cell=['300arcsec','300arcsec'],spw='0:150~350,0:400~700')

if 1:    
    gaincal(mspr, caltable="K5", gaintype='K', solint='inf',  refant="10",  minsnr=1, spw='0:100~130,0:400~600')
    gaincal(mspr, caltable="G5", gaintype='G', solint='inf',  refant="10",  minsnr=2, calmode='ap', gaintable="K5")

if 1:
    applycal(mspr, gaintable=["K5", "G5"])

if 0:
    clean(mspr, "test23", niter=1000, mode="mfs", nterms=1, imsize=[600,600], cell=['300arcsec','300arcsec'], spw='0:150~350,0:400~700')

if 0: # Long baselines only
    clean(mspr, "longb", niter=1000,
          mode="mfs",
          nterms=1,
          imsize=[600,600],
          cell=['300arcsec','300arcsec'],
          spw='0:150~350,0:400~700',
          uvrange="25~1000")

if 0: 
    clean(mspr, "longb-cube", niter=50,
          mode="channel",
          width=10,
          imsize=[600,600],
          cell=['300arcsec','300arcsec'],
          spw='0:150~350,0:400~700', weighting="briggs", robust=0)        

if 0:    
    uvcontsub(mspr, fitspw='0:100~130,0:400~600', solint="inf", fitorder=1, want_cont=True)

if 0:    
    bandpass(mspr, caltable="B5", solnorm=True,  gaintable=["K5", "G5"] , refant="10", minsnr=3)

if 0: # Restrict to short baselines     
    bandpass(mspr, caltable="B5", solnorm=True,  gaintable=["K5", "G5"] , refant="10", minsnr=3, uvrange="0~30")    

if 0:
    bandpass(mspr, caltable="B5-indx", solnorm=True,  gaintable=["K5", "G5"] , refant="10", minsnr=3)    


if 0:
    plotcal("B3", xaxis="chan", yaxis="phase")

    applycal(mspr, gaintable=["B4", "K4", "G4"])

if 0:

    gaincal("/fast/temp/casaclosure3/GC-pr.ms", caltable="g16", gaintype='K', solint='inf',  refant="10", spw='0:100~130,0:400~600', minsnr=1)

    gaincal("/fast/temp/casaclosure3/GC-pr.ms", caltable="g17", gaintype='G', solint='inf',  refant="43", spw='0:400~600', minsnr=2, calmode='ap', gaintable="g16")
    applycal("/fast/temp/casaclosure3/GC-pr.ms", gaintable=["g16", "g17"])

    clean("/fast/temp/casaclosure3/GC-pr.ms", "test", niter=1000, mode="mfs", imsize=[400,400], cell=['300arcsec','300arcsec'],spw='0:100~130,0:400~600')


# Create slopint GC

if 0:
    cl.addcomponent(flux=1.0, fluxunit='Jy',shape='point', dir='J2000 17h45m40.0409s -29d0m28.118s', spectrumtype='spectral index', index=-1.0)  
    cl.rename("GC-indx.cl")
    cl.close()  
