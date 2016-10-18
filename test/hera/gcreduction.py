# Notes on GC data-reduction

import clplot.clquants as clquants

msin="/fast/temp/t/GC.ms"
importuvfits("/data/archive/HERA-5/zen.2457545.48707.xx.HH.uvcU.uvfits", msin)
# This is essential. A routine in clplot.clquants
clquants.reorrder(msin)
ft(msin, complist="GC.cl", usescratch=True)

mspr="/fast/temp/t/GC-pr.ms"

fixvis(msin, mspr, phasecenter="J2000 17h45m40s -29d00m28s")

flagdata(mspr, flagbackup=T,        mode='manual', antenna="82")

if 0:
    gaincal(mspr, caltable="g18", gaintype='G', solint='inf',  refant="43", spw='0:400~600', minsnr=2, calmode='ap', gaintable="g16")
    applycal(mspr, gaintable=["g16", "g18"])
    clean(mspr, "test3", niter=1000, mode="mfs", nterms=1, imsize=[400,400], cell=['300arcsec','300arcsec'],spw='0:150~350,0:400~700')

gaincal(mspr, caltable="K4", gaintype='K', solint='inf',  refant="10", spw='0:100~130,0:400~600', minsnr=1)
gaincal(mspr, caltable="G4", gaintype='G', solint='inf',  refant="10", spw='0:100~130,0:400~600', minsnr=2, calmode='ap', gaintable="K4")

if 0:
    applycal(mspr, gaintable=["K4", "G4"])

bandpass(mspr, caltable="B4", solnorm=True,  gaintable=["K4", "G4"] , refant="10", minsnr=3)

if 0:
    plotcal("B3", xaxis="chan", yaxis="phase")

applycal(mspr, gaintable=["B4", "K4", "G4"])

if 0:

    gaincal("/fast/temp/casaclosure3/GC-pr.ms", caltable="g16", gaintype='K', solint='inf',  refant="10", spw='0:100~130,0:400~600', minsnr=1)

    gaincal("/fast/temp/casaclosure3/GC-pr.ms", caltable="g17", gaintype='G', solint='inf',  refant="43", spw='0:400~600', minsnr=2, calmode='ap', gaintable="g16")
    applycal("/fast/temp/casaclosure3/GC-pr.ms", gaintable=["g16", "g17"])

    clean("/fast/temp/casaclosure3/GC-pr.ms", "test", niter=1000, mode="mfs", imsize=[400,400], cell=['300arcsec','300arcsec'],spw='0:100~130,0:400~600')
