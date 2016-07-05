
if 0:
    cl=casac.casac.componentlist()
    cl.addcomponent(dir="J2000 10h00m00.00s -30d00m00.0s",
                    flux=2.0,
                    fluxunit='Jy',
                    freq='230.0GHz',
                    shape="Gaussian",
                    majoraxis="0.1arcmin",
                    minoraxis='0.05arcmin',
                    positionangle='45.0deg')
    cl.rename('Gauss_point.cl')
    cl.done()

# Has to run in plain CASA
simobserve(project = "t1.ms",
                complist = 'Gauss_point.cl',
                compwidth = '1GHz',
                direction = "J2000 10h00m00.0s -30d00m00.0s" ,
                obsmode = "int",
                antennalist = 'alma.cycle0.compact.cfg',
                totaltime = "1000s",
                mapsize = "10arcsec")

a=closureAmp("/home/bnikolic/n/casata/clplot/t1.ms/t1.ms.alma.cycle0.compact.ms", alist=[2,3,4,5])
ampTime(a["amp"][0])
plt.show()


