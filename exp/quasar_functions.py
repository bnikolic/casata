#written by Sarah Graves, October 2011

import numpy as np

#get casa tasks and tools from casata
import casata.tools.ctools
from casata.tools.vtasks import *



_script_log_level=1

#function to print info to screen depending on logging values
#Prob not needed, 
def showinfo(message, level):
    try:
        global _script_log_level
    except NameError:
        _script_log_level = 1
        
    if level <= _script_log_level:
        print message




# spw 0 = wvr data 
# spw 1,3,5, 7 == proper data 
# spw 2,4,6,8 -- average?
# or one channel? from corresponding real spectral windows.


#ODO: use casata, prob should break up into separate functions
def get_vis_info(myvis, spws=[1,3,5,7]):
    """
    For a given visability and choice of science spws,
    get the:
    antennas
    field names
    field ids
    number of channels per SPW
    longest baseline

    Takes in the name of the measurement set, and the list of science
    SPWs that the user wishes to reduce.

    Returns a tuple of the:
    
    antennas, fields, field_ids, spw_chandict, spw_freqdict, 
              band, max_baseline

    *antennas* and *field_ids* are numpy arrays of strings

    *field_ids* is a numpy array of floats. 

    *spw_chandict* and spw_freqdict* are dictionaries, with the SPW
    identifiers as keys, and the number of channels or the reference
    frequency (respectively) of the spw as the values.

    *band* is a single float representing the ALMA band based on a
    built-in list of frequency ranges. 

    *max_baseline* represents the longest physical baseline (in m)
    between any two of the antennae.

    NOTE THAT THE MAXIMUM BASELINE CALCULATION DOESN'T CHECK IF YOU
    HAVE FLAGGED THAT ANTENNA AT A LATER POINT!

    """

    #open the measurement set
    ms=casata.tools.ctools.get("ms")
    ms.open(myvis)

    #get the values that are constant for all spws (antenna names,
    #field names and field_ids)
    antennas=ms.range(items='antennas')['antennas']
    fields=ms.range(items='fields')['fields']
    field_ids=ms.range(items='field_id')['field_id']

    field_dict=dict( zip( field_ids, fields))

    nchans=[]
    rfreqs=[]
    lo_freq=[]
    hi_freq=[]

    #get the values that can vary with spw -- number of channels, the
    #reference frequency, and the frequency of each channel
    for i in spws:
        ms.selectinit(datadescid = i)
        ranges=ms.range(items = ['num_chan','ref_frequency','chan_freq'])
        number_channels = ranges['num_chan']
        ref_frequency = ranges['ref_frequency']
        chan_freq = ranges['chan_freq']
        nchans.append(number_channels.item())
        rfreqs.append(ref_frequency.item())
        lo_freq.append(chan_freq[0].item())
        hi_freq.append(chan_freq[-1].item())

    #close the measurement set
    ms.close()

    #dictionary with number of channels per spw
    spw_chandict=dict( zip( spws, nchans ) )
    spw_freqdict=dict( zip( spws, rfreqs ) )
    spw_lofreqdict=dict( zip( spws, lo_freq ) )
    spw_hifreqdict=dict( zip( spws, hi_freq ) )


    #alma bands:
    almabands={3: [84,116],
               6: [211,275],
               7: [275,373],
               9: [602,720]}

    bands=[]
    for spw in spws:
        freq=spw_freqdict[spw]*1e-9#convert to GHz

        #check which band spw frequency is within
        lower_lim=np.asarray([almabands[band][0] for band in almabands])
        higher_lim=np.asarray([almabands[band][1] for band in almabands])
        bandlist=np.asarray([ band for band in almabands])
        bands.append(bandlist[np.logical_and(lower_lim < freq, 
                                     higher_lim > freq)].item())


    spw_banddict=dict( zip( spws, bands ) )

    #check that all the spws should be in same band?
    band=spw_banddict[1]
    if len( set (spw_banddict.values() ))==1:
        showinfo('All spws in same band', 2)
        band=spw_banddict.values()[0]
        showinfo('Band is: '+str(band), 1)
    else:
        print 'WARNING: NOT ALL SPWS IN SAME BAND!'
        print 'This may represent a programming error by the author...'


    #get (physical) baselines
    tb=casata.tools.ctools.get("tb")
    tb.open(myvis+'/ANTENNA')
    positions=tb.getcol('POSITION')
    names=tb.getcol('NAME')
    tb.close()
    
    baselines=[]
    antenna_pos=dict(zip(names,np.swapaxes(positions,0,1)))
    for ant1 in names:
        for ant2 in names:
            baseline=get_baseline(antenna_pos[ant1], antenna_pos[ant2])
            baselines.append(baseline)
                                 
    #for moment, return only the max baseline?
    max_baseline=max(baselines)

    return (antennas, field_dict, 
            spw_chandict,spw_freqdict, 
            band, max_baseline)


radians_in_arcseconds=206264.806

def get_baseline(pos1, pos2):

    """
    Return the distance between two positions, *pos1* and *pos2*

    """
    return np.sqrt(np.sum((pos1-pos2)**2))


def antpos_to_dict(ant_names, ant_corrs):
    """
    function to turn comma separated string of antenna names, and a
    list of floats representing the antenna corrections to those
    antenna's into a dictionary

    """
    
    ant_names=ant_names.split(',')
    ant_corr=np.asarray(ant_corr)
    ant_corr=ant_corr.reshape([len(ant_corr)/3,3])
    return dict( zip( ant_names, ant_corr))
    

def  antenna_position_correct(vis, antenna_position_corrections, antpos_caltable):
    """
    Read in dictionary of antenna positions, calculate caltable for vis,
    and return the name of the caltable

    """

    #get names and corrections as lists
    antenna_names=antenna_position_corrections.keys()
    antenna_corrections=antenna_position_corrections.values()

    #calculate the calibration table
    gencal(vis=vis, caltable=antpos_caltable, caltype='antpos',
           antenna=antenna_names, parameter=antenna_corrections)
    
    #return the name of the position table
    return antpos_caltable

def call_wvrgcal(vis, wvrgcal_table, wvrgcal, field_dict, cal_field, antennas
                 **wvrgcal_options
                 ):
    """
    Call a given wvrgcal binary with specified options.

    vis: the name of the measurement set (string, representing an ms)

    wvrgcal_table: name of caltable to be produced by wvrgcal

    wvrgcal: string representing the wvrgcal_binary (if True, then
    uses the first 'wvrgcal' found in system path)

    wvrgcal_options: dictionary of keyword options passed to wvrgcal

    """

    #if no specific binary given, use the first one in the system path
    if wvrgcal is True:
        wvrgcal='wvrgcal'

    #set up options used in the fields
    if wvrgcal_options.has_key('tie_all'):
        wvrgcal_options.pop('tie_all')
        wvrgcal_options['tie']=string_creator(field_dict.values())
            
    if wvrgcal_options.has_key('stat_cal'):
        wvrgcal_options.pop('stat_cal')
        wvrgcal_options['statsource']=field_dict[cal_field]
    
    #flag antenna without wvr0? TV?
    #TODDO

    #set up wvrgcal
    mywvrgcal = calling_wvrgcal.wvrgcal(wvrgcal)
    
    #call wvrgcal
    mywvrgcal.call(ms=vis, output=wvrgcal_table, **wvrgcal_options)

    #return the output caltable and the version number
    return wvrgcal_table, mywvrgcal.version

                 

#based on freq
#pixsize and im_size

def get_imaging_params(freq, max_baseline):
    """Get appropriate pixel and image size, based on beam."""

    #I'm not sure what we need yet, so just ignoring this for the moment.
    #Will pixel size depend on size of synthesized beam?
    #need to cover primary beam
    #NOT YET DONE

    pixsize=radians_in_arcseconds*(3e8/freq)/max_baseline
    im_size=512
    return pixsize, im_size


#function to turn list or array into comma-separated string for giving
#to wvrgcal caller (i.e. for '--wvrflag' and '--tie' options)
def string_creator(names):
    """Create appropriate string of source names to tie sources
    together for wvrgcal_caller, or antenna names to flag for same.

    sourcenames should be a list or array of source names to be
    tied, or a list or array of."""
    if not isinstance(names, basestring):
        try:
            tiestring=','.join(names)
        except TypeError:
            names=[str(i) for i in names]
            tiestring=','.join(names)
    else:
        tiestring=names
    return tiestring

    
def apriori_flagging(vis, quackinterval=1.5, quackincrement=True):

    """
    Perform apriori flagging that will be carried out on all data.

    """

    #flag the autocorrelations
    flagautocorr(vis=vis)
    
    #flag any data that is shadowed
    flagdata(vis=vis, mode='shadow', flagbackup=False)

    #quack the data
    flagdata(vis=vis, flagbackup=False, mode='quack', 
             quackinterval=quackinterval,
             quackincrement=True)

    #back up data after apriori flagging
    #TODO: remove this backup?
    #flagmanager(vis=vis, mode='save', versionname='apriori',
    #x            comment = 'After, autocorr, shadow, and quack.')

def flagging_spw_ends(spw_chandict, method='percent', flagrange=10):

    """
    Create spw flagging string for ending to flagdata.

    spw_chandict is dictionary of spw indices and the number of
    channels in them

    Method can be 'percent' or 'chosen'

    'percent' will return a string that willflag flagrange% at the
    beginning and ends of every spw.

    'chosen' will simply return the string given in flagrange

    """
    spw_flagging=[]

    if method.lower().strip() == 'percent':
        for spw in spw_chandict:
            channels=spw_chandict[spw]
            flag_num=int(round( (flagrange/100.0) * channels))
            spw_flagging.append(str(spw)+':0~'+str(flag_num - 1)+ 
                                ';'+str(channels-flag_num)
                                +'~'+str(channels-1) )
    
    elif method.lower().strip() == 'chosen':
        spw_flagging=flagrange
    
    else:
        raise KeyError
    
    return spw_flagging



#TODO: BEST WAY TO THINK about plots? -- what types of plots are
# needed in general, rather than at what stage of data processing?

#runs, produces plots with data, need to check if these are the most
#useful plots we could be creating.
def corrected_plots(vis, spw_chandict, field_dict, correlations, plotroot, 
                    figext='png',avgtime='1e8',
                    interactive=False, overwrite=True): 

    """ Make plots of the corrected data

    *vis*: The visibility data set
    *spw_chandict*: the science spws and number of channels
    *field_dict*: the dictionary of field names
    *correlations*: which correlations to examine, either a single
     string or a list of strings
    *plotroot*: the root name of the plots

    *figext*: type of figure, e.g. 'png' or 'pdf'
    *avgtime*: time to average over in some plots
    *interactive*: do you want to interact with the plot?
    *overwrite*: do you want to overwrite existing plots of the same name?
     
    
    plots of:

    amplitude vs time, per spw and per correlation (color the fields)

    amplitude vs uvdist, per field and per correlation (color the spws)

    WARNING: this uses plotms, and at the moment (October 2011) this
    will not work without opening a gui -- therefore these commands
    willl not succeed if there is no X11 session. This will be true
    regardless of what the keyword *interactive* is set to
    
    """
    print '---- MAKING PLOTS OF CORRECTED DATA ----'


    plotms_kwargs=dict(
        vis = vis,
        xaxis = 'time',
        yaxis = 'amp',
        ydatacolumn = 'corrected',
        coloraxis = 'field',
        interactive = interactive,
        format=figext,
        overwrite=overwrite)

    plotms_kwargs['avgchannel']=string_creator(spw_chandict.values())
    plotname=plotroot+'_'+plotms_kwargs['xaxis']+'_vs_'+plotms_kwargs['yaxis']
    #amplitude vs time, per spw and per correlation
    for correlation in correlations:
        plotms_kwargs['correlation']=correlation
        for spw in spw_chandict.keys():
            plotms_kwargs['spw']=str(spw)
            plotms_kwargs['plotfile']=plotname+'_spw'+str(spw)+'_'+correlation+'.'+figext
            plotms_kwargs['title']='Amp vs. Time\n'+str(vis)+'\nSPW: '+str(spw)+' Corr: '+correlation
            plotms(**plotms_kwargs)

            print '....'+plotms_kwargs['plotfile']

    #amplitude vs uvdist, one field per plot, colors spw
    plotms_kwargs['xaxis']='uvdist'
    plotms_kwargs['avgtime']=avgtime
    plotname=plotroot+'_'+plotms_kwargs['xaxis']+'_vs_'+plotms_kwargs['yaxis']
    #TODO: does this work if they have

    plotms_kwargs['coloraxis']='spw'
    plotms_kwargs['spw']=''
    for correlation in correlations:
        plotms_kwargs['correlation']=correlation
        for field in field_dict.values():
            plotms_kwargs['field']=field
            plotms_kwargs['plotfile']=plotname+'_f_'+field+'_'+correlation+'.'+figext
            plotms_kwargs['title']='Amp vs. UVdist\n'+str(vis)+'\nfield: '+field+' Corr: '+correlation
            plotms(**plotms_kwargs)
            print '....'+plotms_kwargs['plotfile']



    


#works.
def make_box_and_mask(im_size, mask_dx, mask_dy=None):
    """
    Create the box string for stats images, and the mask vertices
    for cleaning the image and fitting the image.

    im_size: Size of image in pixels 

    mask_dx: length of mask in x direction, in pixels

    mask_dy: lenght of mask in y direction, in pixels. if None, this
    will be the same as mask_dx (using a square mask)

    returns box, mask

    """

    if not mask_dy:
        mask_dy=mask_dx
    box = str(20)+','+str(int(im_size*0.625))+','+str(im_size-20)+','+str(im_size-20)
    x1 = im_size/2 - mask_dx/2
    x2 = im_size/2 + mask_dx/2
    y1 = im_size/2 - mask_dy/2
    y2 = im_size/2 + mask_dy/2
    mask = [x1, y1, x2, y2]

    return box, mask



def clean_data(vis, pixsize, im_size, n_iter, field_dict,
               cleanweighting, cleanspw, cleanmode):
    print '---- CLEANING ----'
    
    clean_kwargs=dict(vis=vis, cell=pixsize, imsize=im_size,
                      niter = n_iter,
                      stokes = 'IQUV',
                      weighting = cleanweighting,
                      robust = 0.0,
                      spw = cleanspw,
                      mode = cleanmode,
                      mask = [x1, y1, x2, y2])

    imagenames=[]
    for field in field_dict.values():
        clean_kwargs['imagename']=root+'f'+field
        clean(**clean_kwargs)
        imagenames.append(clean_kwargs['imagename'])

    return imagenames


#checked, it seems to work
def create_fits_images(imagenames):

    """
    Create fits version of images.

    Take in a list of images.

    Return a list of fits files.

    """
    print '---- EXPORTING FITS (I,Q,U,V) IMAGES ----'

    fitslist=[]
    for imname in imagenames:
        fitsimage=imname+'.fits'
        exportfits(imagename=imname, fitsimage=imname+'.fits')
        fitslist.append(fitsimage)
    return fitslist


#checked that this works, not checked the detailed results.
def stats_images(imagenames, bx,logfile=None):
    """
    Function to calculate the statistics on the images.

    Takes in list of images, the box to calculate statistics on.
    Prints out statistics to screen, and optionally to a log file.

    """

    #TODO:
    #CHECK replicates Marcels version, no errors introduced.
    
    print '---COMPUTING STATS ----'

    if logfile:
        myfile=open(logfile, 'a')
        myfile.write('-----------COMPUTING STATS ON IMAGES---------\n')
    for imname in imagenames:
        #get stokes I, Q, U and V
        obj = imhead(imname, mode='get', hdkey='object')
        st = 'I'
        gstat_I = imstat(imname, stokes=st)
        bgstat_I = imstat(imname, stokes=st, box=bx)
        st = 'Q'
        gstat_Q = imstat(imname, stokes=st)
        bgstat_Q = imstat(imname, stokes=st, box=bx)
        st = 'U'
        gstat_U = imstat(imname, stokes=st)
        bgstat_U = imstat(imname, stokes=st, box=bx)
        st = 'V'
        gstat_V = imstat(imname, stokes=st)
        bgstat_V = imstat(imname, stokes=st, box=bx)
        stats_string=str(str(obj['value'])+'\n'
                         +'ST            MAX               MIN                RMS              OMIN       MAX/RMS\nI  '
                         +str(gstat_I['max'][0])+'  '+ str(gstat_I['min'][0])+'  '+str(bgstat_I['rms'][0])+'  '+str(bgstat_I['min'][0])+'  '+str(gstat_I['max'][0]/bgstat_I['rms'][0])+'\n'
                         +'Q  '+str(gstat_Q['max'][0])+'  '+str(gstat_Q['min'][0])+'  '+str(bgstat_Q['rms'][0])+'  '+str(bgstat_Q['min'][0])+'  '+str(gstat_Q['max'][0]/bgstat_Q['rms'][0])+'\n'
                         +'U  '+str(gstat_U['max'][0])+'  '+str(gstat_U['min'][0])+'  '+str(bgstat_U['rms'][0])+'  '+str(bgstat_U['min'][0])+'  '+str(gstat_U['max'][0]/bgstat_U['rms'][0])+'\n'
                         +'V  '+str(gstat_V['max'][0])+'  '+str(gstat_V['min'][0])+'  '+str(bgstat_V['rms'][0])+'  '+str(bgstat_V['min'][0])+'  '+str(gstat_V['max'][0]/bgstat_V['rms'][0]))

        print stats_string

        if logfile:
            myfile.write(stats_string+'\n')
    if logfile:
        myfile.close()


def imfit_images(imagenames, mask, logfile=None):
    """
    Carry out imfit routine on given images, using an imfit box
    specified by *mask* = [x1, y1, x2, y2].  

    Print the resulting image flux and shape to the screen, and
    optionally append to a logfile specified in *logfile*
    
    """
    #TODO:
    #CHeck replicates Marcel's verison

    print '---- RUNNING IMFIT ON STOKES I IMAGES ----'
    if logfile:
        myfile.write('\n\n ---- RUNNING IMFIT ON STOKES I IMAGES ----\n')

    #get box values in expected format
    imfitbox=','.join(str(value) for value in mask)

    #go through each image
    for imname in imagenames:
        print imname
        if logfile:
            myfile.write(imname+'\n')

        #do imfit
        fit_vals = imfit(imname, box=imfitbox, stokes = 'I')

        #get flux and shape
        flx = fit_vals['results']['component0']['flux']
        shp = fit_vals['results']['component0']['shape']

        #get the values and print to screen and logfile (if requested)
        imfit_string=str('Flux: ' + str(round(flx['value'][0],4))+' +/- '
                         +str(round(flx['error'][0],5)) +'\n'
                         + 'Major axis FWHM: ' + str(round(shp['majoraxis']['value'],3))
                         +' +/- '+str(round(shp['majoraxiserror']['value'],4)) +'\n'
                         + 'Minor axis FWHM: ' + str(round(shp['minoraxis']['value'],3))
                         +' +/- '+str(round(shp['minoraxiserror']['value'],4)) +'\n'
                         + 'PA: ' + str(round(shp['positionangle']['value'],1)))

        
        print imfit_string

        if logfile:
            myfile.write(imfit_string+'\n')
    if logfile:
        myfile.close()

