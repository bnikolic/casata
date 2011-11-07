#written by Sarah Graves, October 2011

import numpy as np
import os
import shutil
import fnmatch
import subprocess

#get casa tasks and tools from casata
import casata.tools.ctools
from casata.tools.vtasks import *
import calling_wvrgcal

#matplotlib
import matplotlib
import matplotlib.pyplot as plt

#create unique log names
import logging
import tempfile

#create csv output files
import csv

def create_log_file(root_name, mode='w', tag=None):
    """create a logfile with a unique name, opened in the specified
    mode, using the root_name as the prefix, and optionally with
    '_'+tag added to the prefix.

    Returns the tempfile object 'mylogfile: the python file object
    is in mylogfile.file, and the name of the file is in
    mylogfile.name

    """
    prefix=root_name+'_'
    if tag:
        prefix=prefix+tag+'_'
    mylogfile=tempfile.NamedTemporaryFile(mode=mode, prefix=prefix,
                                          suffix='.log', dir=os.getcwd(), delete=False) 

    return mylogfile




#TODO: logging? want all parameters used to be recorded in output file.
#TODO: think about versiosning

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


#write shorter versions of the stuff inside get_visinfo...
def get_antenna_names(vis):
    """
    get the antennas listed within a measurement set.
    """
    
    ms=casata.tools.ctools.get("ms")
    ms.open(vis)
    antennas=ms.range(items='antennas')['antennas']
    ms.close()
    
    return antennas

def get_field_dictionary(vis):
    """
    Return a dictionary containing the numerical field ID's as keys,
    and the string field names as values, from a measurement set

    """    
    #open the measurement set
    ms=casata.tools.ctools.get("ms")
    ms.open(vis)
    
    #get field names and ids
    fields=ms.range(items='fields')['fields']
    field_ids=ms.range(items='field_id')['field_id']
    
    #close the measuremnt set
    ms.close()
    
    #create dictionary
    field_dict=dict( zip( field_ids, fields))
    
    return field_dict

def get_spw_channel_dictionary(vis, spws=[1,3,5,7]):
    """
    Return a dictionary containing the numerical spw ID's as keys,
    and the numerical number of channels in that spw as values, from a measurement set

    """    
    #open the measurement set
    ms=casata.tools.ctools.get("ms")
    ms.open(vis)
    
    nchans=[]
    
    #go through each requested spw
    for i in spws:
        ms.selectinit(datadescid = i)
        ranges=ms.range(items = ['num_chan','ref_frequency','chan_freq'])
        number_channels = ranges['num_chan']
        nchans.append(number_channels.item())
    
    #close the measurement set
    ms.close()
    
    #create dictionary
    spw_chan_dict=dict( zip( spws, nchans))
    
    return spw_chan_dict

def get_spw_frequency(vis, spws=[1,3,5,7]):
    """
    Return a dictionary containing the numerical SPW ID's as keys, and
    the numerical frequency of the SPW as values, from measurement set
    vis.

    """
    #open the measurement set
    ms=casata.tools.ctools.get("ms")
    ms.open(vis)

    freqs=[]
    for i in spws:
        ms.selectinit(datadescid = i)
        ranges=ms.range(items = ['ref_frequency'])    
        frequency = ranges['ref_frequency']
        freqs.append( frequency.item() )
    
    ms.close()
    
    spw_freq_dict=dict( zip( spws, freqs ) )
    
    return spw_freq_dict

#TODO:prob should break up into separate functions
def get_vis_info(myvis, spws=[1,3,5,7], logging=None ):
    """
    For a given visability and choice of science spws,
    get the:
    antennas
    field names
    field ids
    number of channels per SPW
    frequencies per spw
    longest baseline

    Takes in the name of the measurement set, and the list of science
    SPWs that the user wishes to reduce.

    Returns a tuple of the:
    
    antennas, field_dict, spw_chandict, spw_freqdict, 
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
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    #open the measurement set
    ms=casata.tools.ctools.get("ms")
    ms.open(myvis)

    mylog.info('Data set', myvis)
    mylog.info('Req. SPWS', str(spws) )

    #get the values that are constant for all spws (antenna names,
    #field names and field_ids)
    antennas=ms.range(items='antennas')['antennas']
    mylog.info('Antennas', str(antennas))

    fields=ms.range(items='fields')['fields']


    field_ids=ms.range(items='field_id')['field_id']
    field_dict=dict( zip( field_ids, fields))
    mylog.dictprint('Fields',field_dict, format1='d', format2='s')


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

    mylog.dictprint('SPW Freq dict',spw_freqdict,format2='.3F', 
                    units='GHz', valueconstant=1e-9 )
    mylog.dictprint('SPW Chan dict', spw_chandict)
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
    #band=spw_banddict[0]
    if len( set (spw_banddict.values() ))==1:
        #showinfo('All spws in same band', 2)
        band=spw_banddict.values()[0]
        #showinfo('Band is: '+str(band), 1)
    else:
        print 'WARNING: NOT ALL SPWS IN SAME BAND!'
        print 'This may represent a programming error by the author...'
        band = spw_banddict

    mylog.info('Band',str(band) )

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
    mylog.info('Max Baseline','%.3F'%max_baseline)
    mylog.message('\n')


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
    ant_corrs=np.asarray(ant_corrs)
    ant_corrs=ant_corrs.reshape([len(ant_corrs)/3,3])
    return dict( zip( ant_names, ant_corrs))
    

def  antenna_position_correct(vis, antenna_position_corrections, antpos_caltable, 
                              logging=None):
    """
    Read in dictionary of antenna positions, calculate caltable for vis,
    and return the name of the caltable

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    mylog.header('Antenna position correction')
    #get names and corrections as lists
    antenna_names=string_creator(antenna_position_corrections.keys() )
    antenna_corrections=list(np.asarray(antenna_position_corrections.values()).flatten())
    mylog.dictprint('Ant Corr',antenna_position_corrections)


    #calculate the calibration table
    gencal(vis=vis, caltable=antpos_caltable, caltype='antpos',
           antenna=antenna_names, parameter=antenna_corrections)
    mylog.info('Caltable', antpos_caltable)
    mylog.message('')

    #return the name of the position table
    return antpos_caltable

def call_wvrgcal(vis, wvrgcal_table, wvrgcal, field_dict, cal_field, antennas,
                 logging=None,
                 **wvrgcal_options):
    """
    Call a given wvrgcal binary with specified options.

    vis: the name of the measurement set (string, representing an ms)

    wvrgcal_table: name of caltable to be produced by wvrgcal

    wvrgcal: string representing the wvrgcal_binary (if True, then
    uses the first 'wvrgcal' found in system path)

    wvrgcal_options: dictionary of keyword options passed to wvrgcal

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    mylog.header('WVRGCAL')
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
    mylog.info('WVRGCAL Version', mywvrgcal.version)

    
    #call wvrgcal
    mywvrgcal.call(ms=vis, output=wvrgcal_table, **wvrgcal_options)
    mylog.dictprint('WVRGCAL options', wvrgcal_options, format1='s', format2='s')
    mylog.info('WVRGCAL caltable', wvrgcal_table)
    mylog.message('')
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

    pixsize=0.25*radians_in_arcseconds*(3e8/freq)/max_baseline
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

    
def apriori_flagging(vis, quackinterval=1.5, quackincrement=True, logging=None):

    """
    Perform apriori flagging that will be carried out on all data.

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging
    mylog.message('Apriori flagging')

    #flag the autocorrelations
    flagautocorr(vis=vis)
    mylog.message('Autocorrelations were flagged')
    #flag any data that is shadowed
    flagdata(vis=vis, mode='shadow', flagbackup=False)
    mylog.message('Shadowed data was flagged')
    #quack the data
    flagdata(vis=vis, flagbackup=False, mode='quack', 
             quackinterval=quackinterval,
             quackincrement=True)
    mylog.message('Data set was "quacked", with quackincrement='+str(quackincrement)+
                  ' and quackinterval='+str(quackinterval)+'\n')


def flagging_spw_ends(vis, spw_chandict, band, logging=None):
    """
    Perform flagging of the beginning and end channels of the spw,
    dependent on the Band of the spws.

    TODO:CURRENTLY HARDCODED, NEED TO DECIDE ON APPROPRIATE METHOD!
    URGENT!
    
    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    # if int(band) == 6:
    #     spw_chans =['*:0~5','*:62~63']
    #     spw_chans=['*:0~3']
    # elif int(band) == 3:
    #     #flag first 7 channels
    #     spw_chans =['*:0~6']
        
    # elif int(band) == 9 and spw_chandict.keys()==[0,1,2,3]:
    #     spw_chans = string_creator(['0:0~7', '1:0~11', '2:0~19', '3:0~13;59~60;63'])

    #do first and last 10%?
    spw_chans=flagging_spw_ends_flagstringcreator(spw_chandict, method='percent',
                                                  flagrange=10)

    #if band 9, do 20%?
    if int(band) == 9:
        spw_chans = flagging_spw_ends_flagstringcreator(spw_chandict, method='percent',
                                                  flagrange=15)
    flagdata(vis=vis, flagbackup=False, spw=spw_chans)
    
    mylog.message('Flagging beginning and end spw channels')
    mylog.message('Channel string: '+str(spw_chans)+'\n')




def flagging_spw_ends_flagstringcreator(spw_chandict, method='percent', flagrange=10):

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


def initial_plots(vis, spws, correlations, root_name, 
                  overwrite=True, interactive=False, figext='png', logging=None):
    """
    Produce plot of amp versus channel for each SPW provided.

    All fields are shown on same plot, and the correlations are
    written in different colours

    Return list of plots produced

    """

    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging
    mylog.header('Initial plots', punctuation='-')
    correlations=string_creator(correlations)
    plot_kwargs=dict( vis=vis, xaxis='channel', yaxis='amp', field='',
                          avgtime='1e8', correlation='XX,YY', coloraxis='corr',
                          overwrite=overwrite)

    output_plots=[]
    fig_file_root=root_name+'00_initial_amp_vs_chan_spw'
    for spw in spws:
        filename=fig_file_root+str(spw)+'.'+figext
        plot_kwargs['plotfile']=filename
        plot_kwargs['spw']=str(spw)
        plotms(**plot_kwargs)
        output_plots.append(filename)
    
    
    mylog.plots_created('Amp vs Channel, per spw', output_plots)
    return output_plots


def spw_channel_marking_fraction(spw_chandict, begin_frac, end_frac):
    """
    Create string selecting channels from beginning fraction to
    end_fraction (inclusive).

    Return string that will select those channel in casa tasks

    """

    spw_chanstring=[]
    for spw in spw_chandict:
        n_chans=spw_chandict[spw]
        spw_chanstring.append(str(spw)+':'
                              +str(int(round(n_chans/begin_frac)))
                              +'~'
                              +str(int(round(n_chans/end_frac)))
                              )
    return string_creator(spw_chanstring)

def get_post_split_spw_chandict(spw_chandict):
    """
    Get chandict representing chosen spws after splitting

    """
    spws=spw_chandict.keys()
    post_split_spws=range(0, len(spws))
    post_split_spw_chandict={}
    for new,old in zip(post_split_spws, spws):
        post_split_spw_chandict[new]=spw_chandict[old]
    
    return post_split_spw_chandict



def bpp_calibration(vis, bpp_caltable, spw_chandict,
                     cal_field_name, ref_ant, 
                     minsnr=2.0, minblperant=4, solint='60s',
                     begin_frac=3, end_frac=2, logging=None):
    """
    calibrate the phases of the bandpass calibrator.

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging
        
    #print '------ calibrate phases for bandpass calibrator----'
    mylog.header('Bandpass Phase Calibration', punctuation='-')
    mylog.message('Calibrate phases for bandpass calibrator')
    
    spw_chanstring=spw_channel_marking_fraction(spw_chandict, begin_frac, 
                                                end_frac)
    bpp_dictionary=dict(vis=vis, caltable=bpp_caltable, field=cal_field_name,
                            refant=ref_ant, calmode='p', spw=spw_chanstring,
                            minsnr=minsnr, minblperant=minblperant, solint=solint)
    gaincal(**bpp_dictionary)
    mylog.dictprint('Bpp cal options', bpp_dictionary)
    mylog.message('\n')
    return bpp_caltable


def caltable_plot(caltable,spw_chandict, figroot, xaxis='time',
                  phase=None, amp=None, snr=None, 
                  interactive=False,
                  figext='png', correlations=['X','Y'],
                  logging=None, phase_range=[0,0,-180,180]):
    """
    Plots of caltable

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging
    
    mylog.message('Plotting images of '+caltable+'\n')

    
    #print '----plotting '+caltable

    plot_file_root=figroot+caltable.split('_')[-1]
    plot_kwargs=dict( caltable=caltable, xaxis='time', iteration='antenna', 
                      showgui=interactive, subplot=551, plotsymbol=',',
                      fontsize=7 )
    plot_kwargs['xaxis']=xaxis
    plotfiles=[]

    if phase:
        #print '-----plotting phase vs '+xaxis
        plot_kwargs['yaxis']='phase'
        yaxis=plot_kwargs['yaxis']
        plot_kwargs['plotrange']=phase_range
        plot_file = plot_file_root+'_'+yaxis+'_vs_'+xaxis
        plotfiles = plotfiles + plotcal_util(plot_kwargs, spw_chandict.keys(),
                                         correlations, plot_file, figext)
        mylog.plots_created(caltable+': phase vs '+xaxis, plotfiles)
        plotfiles=[]

    if amp:
        #print '-----plotting amp vs '+xaxis
        plot_kwargs['yaxis']='amp'
        yaxis=plot_kwargs['yaxis']
        plot_kwargs['plotrange']=[]
        plot_file = plot_file_root+'_'+yaxis+'_vs_'+xaxis
        plotfiles = plotfiles + plotcal_util(plot_kwargs, spw_chandict.keys(),
                                             correlations, plot_file, figext)
        mylog.plots_created(caltable+': amplitude vs '+xaxis, plotfiles)
        plotfiles=[]

    if snr:
        #print '----- plotting snr vs '+xaxis
        plot_kwargs['yaxis']='snr'
        yaxis=plot_kwargs['yaxis']
        plot_kwargs['plotrange']=[]
        plot_file = plot_file_root+'_'+yaxis+'_vs_'+xaxis

        plotfiles = plotfiles + plotcal_util(plot_kwargs, spw_chandict.keys(), 
                                             correlations, plot_file, figext)
        mylog.plots_created(caltable+': SNR vs '+xaxis, plotfiles)
        plotfiles=[]

    #return plotfiles

def plotcal_util(plot_kwargs, spws, correlations, plot_file_root, figext):
    """
    Utility for creating plotcal figures for each spw and each correlation given.
    
    Trying plotting both correlations on one plot

    """
    plotfiles=[]
    for spw in spws:
        plot_kwargs['spw']=str(spw)
        plot_file=plot_file_root+'_spw'+str(spw)
        #for poln in correlations:
        plot_kwargs['poln']='RL'
        plot_kwargs['figfile']=''
        figfile=plot_file+'.'+figext
        plotcal(**plot_kwargs)
        fig=plt.gcf()
        for ax in fig.axes:
            title=ax.get_title()
            new_title=title.split('Antenna=')[1].replace("'","")
            ax.set_title(new_title,fontsize=7)
            if plot_kwargs['xaxis']=='time':
                for mlines in ax.lines:
                    mlines.set_linestyle('solid')
                    mlines.set_linewidth(0.5)
        plt.draw()
        fig.savefig(figfile, bbox_inches='tight', pad_inches=0.2)
        plotfiles.append(figfile)
    return plotfiles
    

def bandpass_calibration(vis, unapplied_caltables, bp_caltable, cal_field_name,ref_ant,
                         solint='inf', fillgaps=20, minblperant=4, solnorm=True, 
                         combine='scan',
                         logging=None):

    """perform bandpass calibration

    """
    
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging


    print '----BANDPASS CALIBRATION----'
    mylog.header('Bandpass Calibration', punctuation='-')

    bandpass_options=dict(vis=vis, caltable=bp_caltable,
             gaintable=unapplied_caltables,
             field=cal_field_name,
             spw='', combine=combine, solint=solint, minblperant=minblperant, 
             refant=ref_ant,
             solnorm=solnorm)

    bandpass(**bandpass_options)
             

    mylog.dictprint('Bandpass cal options', bandpass_options)
    mylog.message('\n')

    return bp_caltable

def gain_calibration(vis,unapplied_caltables, gc_caltable, gc_amp_caltable, 
                     cal_field_name, ref_ant,
                     solint='inf',  minblperant=4, minsnr=2,
                     logging=None):

    """perform gain calibration
    phase, then amp and phase

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging


    
    #print '-----GAIN CALIBRATION----'
    #print '.... phase'

    mylog.header('Gain Calibration', punctuation='-')

    gcphase_options=dict(vis=vis, field=cal_field_name, gaintable=unapplied_caltables, 
            refant=ref_ant, calmode='p', minsnr=minsnr, minblperant=minblperant, 
            solint=solint, caltable=gc_caltable)
    gaincal(**gcphase_options)

    mylog.dictprint('Gain Calibration Phase cal', gcphase_options)

    unapplied_caltables2=unapplied_caltables[:]
    unapplied_caltables2.append(gc_caltable)

    #print '.... amp and phase'
    gcamp_options= dict(vis=vis, field=cal_field_name, gaintable=unapplied_caltables2, 
            refant=ref_ant, calmode='ap', minsnr=minsnr, minblperant=minblperant,
            solint=solint, caltable=gc_amp_caltable)
    gaincal(**gcamp_options)
    mylog.dictprint('Gain Calibration Amp&Phase cal', gcamp_options)
    mylog.message('\n')
    
    return gc_caltable, gc_amp_caltable
    

def apply_calibrations_calsep(vis, caltables, field_dict, cal_field, logging=None):

    """
    Apply the calibrations, using 'nearest' interpolation on the
    calibration field, and 'linear' interpolation on the science fields.

    TODO: ensure this works if only one source?
    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    #should this be hardcoded?
    #check if right?
    cal_cal_interp=['nearest', 'nearest', 'nearest']
    cal_sci_interp=['nearest', 'linear','linear']

    #get name of calibration field
    cal_field_name = field_dict[cal_field]

    #get a list repeating the name of the calibration field for each gain table
    gain_fields=[cal_field_name for i in caltables]

    #print '----Applying Calibrations:'
    #print '    '+str(caltables)
    #print '...applying to calibration field'
    mylog.header('Applying Calibrations', punctuation='=')

    applycal_dict=dict(vis=vis, field=cal_field_name, interp=cal_cal_interp,
             gaintable=caltables, gainfield=gain_fields,
             flagbackup=False)
    
    applycal(**applycal_dict)
    mylog.dictprint('Applying calibrations to calibration field', applycal_dict)

    science_fields=field_dict.values()[:]
    science_fields.remove(cal_field_name)

    if science_fields:
        
        #print '...applying to science fields'
        field_list=string_creator(science_fields)
        applycal_dict=dict(vis=vis, field=field_list,
                 interp=cal_sci_interp,
                 gaintable=caltables, gainfield=gain_fields,
                 flagbackup=False)
        applycal(**applycal_dict)
        mylog.dictprint('Applying calibrations to science fields', applycal_dict)
    
    mylog.message('\n')
#TODO: BEST WAY TO THINK about plots? -- what types of plots are
# needed in general, rather than at what stage of data processing?

#runs, produces plots with data, need to check if these are the most
#useful plots we could be creating.
def corrected_plots(vis, spw_chandict, field_dict, correlations, plotroot, 
                    figext='png',avgtime='1e8',
                    interactive=False, overwrite=True, logging=None): 

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
    regardless of what the keyword *interactive* is set to.
    
    """
    #print '---- MAKING PLOTS OF CORRECTED DATA ----'
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging
    mylog.header('Plots of Calibrated Data', punctuation='-')
    plot_files=[]
  
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
            plot_files.append(plotms_kwargs['plotfile'])
            #print '....'+plotms_kwargs['plotfile']
    mylog.plots_created('Final data: Amp vs Time', plot_files)
    plot_files2=[]

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
            plot_files2.append(plotms_kwargs['plotfile'])
            #print '....'+plotms_kwargs['plotfile']

    
    mylog.plots_created('Final corrected data: Amp vs UVdist', plot_files2)
    return plot_files+plot_files2
    #end of

    


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



def clean_data(vis, pixsize, im_size, mask,  n_iter, field_dict,
               cleanweighting, cleanspw, cleanmode, root, logging=None):
    #print '---- CLEANING ----'
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging
    mylog.header('Cleaning')
    plotfiles=[]
    clean_kwargs=dict(vis=vis, cell=pixsize, imsize=im_size,
                      niter = n_iter,
                      stokes = 'IQUV',
                      weighting = cleanweighting,
                      robust = 0.0,
                      spw = cleanspw,
                      mode = cleanmode,
                      mask = mask)
    mylog.listprint('Cleaning the fields', field_dict.values())
    mylog.dictprint('Clean Parameters', clean_kwargs)

    imagenames=[]
    for field in field_dict.values():
        clean_kwargs['imagename']=root+'f'+field
        clean_kwargs['field']=field
        #print clean_kwargs
        clean(**clean_kwargs)
        imagenames.append(clean_kwargs['imagename']+'.image')
    mylog.listprint('Cleaned images', imagenames)
    mylog.message('')
    return imagenames


#checked, it seems to work
def create_fits_images(imagenames, logging=None):

    """
    Create fits version of images.

    Take in a list of images.

    Return a list of fits files.

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging
    #print '---- EXPORTING FITS (I,Q,U,V) IMAGES ----'
    mylog.header('Output FITS files')
    fitslist=[]
    for imname in imagenames:
        fitsimage=imname+'.fits'
        exportfits(imagename=imname, fitsimage=imname+'.fits')
        fitslist.append(fitsimage)
    mylog.listprint('FITS (I,Q,U,V) Images', fitslist)
    mylog.message('\n')
    return fitslist


#checked that this works, not checked the detailed results.
def stats_images(imagenames, bx,logging=None, options_call=None):
    """
    Function to calculate the statistics on the images.

    Takes in list of images, the box to calculate statistics on.
    Prints out statistics to screen, and optionally to a log file.

    """

    #TODO:
    #CHECK replicates Marcels version, no errors introduced.
    
    #print '---COMPUTING STATS ----'
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    csv_output=[]
    #mylog.header(' Stats from the final images')
    #mylog.message('\n')
    row=['FIELD', 'stokes', 'maxval', 'minval', 'rms', 'omin', 'max/rms']
    csv_output.append(row)
    #mylog.message('   '.join(row))
    for imname in imagenames:
        obj = imhead(imname, mode='get', hdkey='object')
        field=obj['value']
        for stokes in ['I', 'Q', 'U', 'V']:
            gstat = imstat(imname, stokes=stokes)
            bgstat=imstat(imname, stokes=stokes, box=bx)
            maxval=gstat['max'][0]
            minval=gstat['min'][0]
            rms=bgstat['rms'][0]
            omin=bgstat['min'][0]
            max_rms=gstat['max'][0]/bgstat['rms'][0]
            row=[field, stokes, '%.4G'%maxval, '%.4G'%minval, 
                 '%.4G'%rms, '%.4G'%omin,'%.4G'%max_rms]
            row=[item for item in row]
            csv_output.append(row)
            row_string='   '.join(row)
            #mylog.message(row_string)
        #mylog.message('')
    #mylog.message('\n')
    return csv_output
    
def add_full_run_information_to_table(csv_list, ms_name, wvr_string, wvr_opt_string, quasar_reduction_version, quasar_reduction_opt_string, beams=None):

    """
    for a list of table rows, attach the ms_name to the beginning of
    each row, and the wvr & quasar_reduction versions and options to
    the end of each row.

    """
    csv_output=[]
    headers=csv_list[0]
    field_index=headers.index('FIELD')
    headers.insert(0, 'MS_NAME')
    if beams:
        headers.append('R.BEAM')
    headers.append('WVR_VERSION')
    headers.append('WVR_OPTIONS')
    headers.append('QRED_VERSION')
    headers.append('QRED_OPTIONS')
    csv_output.append(headers)
    for row in csv_list[1:]:
        if beams:
            field=row[field_index]
            beamdict=beams[field]
            beamstr=','.join([str(key)+'='+str(beamdict[key]) for key in beamdict])
            row.append(beamstr)            
        row.insert(0, ms_name)
        row.append(wvr_string)
        row.append(wvr_opt_string)
        row.append(quasar_reduction_version)
        row.append(quasar_reduction_opt_string)
        csv_output.append(row)

            
    return csv_output
        

def imfit_images(imagenames, mask, logging=None):
    """
    Carry out imfit routine on given images, using an imfit box
    specified by *mask* = [x1, y1, x2, y2].  

    Print the resulting image flux and shape to the screen, and
    optionally append to a logfile specified in *logfile*
    
    """

    #print '---- RUNNING IMFIT ON STOKES I IMAGES ----'
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    csv_output=[]
    #mylog.header('IMFIT: fitting  to STOKES I image')
    csv_output.append(['FIELD', 'FLUX','FLUX_ERR', 'MAJ_FWHM', 'MAJ_FWHM_ERR',
                      'MIN_FWHM', 'MIN_FWHLM_ERR','PA'])
    #get box values in expected format
    imfitbox=','.join(str(value) for value in mask)

    #go through each image
    for imname in imagenames:
        mylog.message(imname)
        #get field name
        obj=imhead(imname, mode='get', hdkey='object')
        field=obj['value']
        #do imfit
        fit_vals = imfit(imname, box=imfitbox, stokes = 'I')

        #get flux and shape
        flx = fit_vals['results']['component0']['flux']
        shp = fit_vals['results']['component0']['shape']

        #get the values and print to screen and logfile (if requested)
        flux=str(round(flx['value'][0],4))
        flux_err=str(round(flx['error'][0],5))
        maj_fwhm=str(round(shp['majoraxis']['value'],3))
        maj_fwhm_err=str(round(shp['majoraxiserror']['value'],4))
        min_fwhm=str(round(shp['minoraxis']['value'],3))
        min_fwhm_err=str(round(shp['minoraxiserror']['value'],4))
        pa=str(round(shp['positionangle']['value'],1))
        imfit_string=str('Flux: ' + str(round(flx['value'][0],4))+' +/- '
                         +str(round(flx['error'][0],5)) +'\n'
                         + 'Major axis FWHM: ' + str(round(shp['majoraxis']['value'],3))
                         +' +/- '+str(round(shp['majoraxiserror']['value'],4)) +'\n'
                         + 'Minor axis FWHM: ' + str(round(shp['minoraxis']['value'],3))
                         +' +/- '+str(round(shp['minoraxiserror']['value'],4)) +'\n'
                         + 'PA: ' + str(round(shp['positionangle']['value'],1)))

        row=[field, flux, flux_err, maj_fwhm, maj_fwhm_err, min_fwhm, min_fwhm_err,
             pa]
        #mylog.message( imfit_string )
        #mylog.message('')
        #mylog.listprint('imfit values',row)
        #mylog.message('')
        csv_output.append(row)
        
    return csv_output






    
class mylogger(object):
    
    def __init__(self, root_name='test', output_file=True, tag=None,
                 console=True, std_logging=None, logfile=None):

        #set up ouput file, unless turned off.
        if output_file and not logfile:
            output_file=create_log_file(root_name, mode='w', tag=None)
            self.output_file=output_file.name
            output_file.close()
        elif output_file and logfile:
            self.output_file=logfile
        else:
            self.output_file=None
        
        #set up logging to console
        if console:
            self.toconsole=True
        else:
            self.console=None

        #setup standard logging
        if std_logging:
            self.std_logging=True
        else:
            self.std_logging=None
            
            
    def write(self, thestring):
        if self.output_file:
            output_file=open(self.output_file, 'a')
            output_file.write(thestring+'\n')
            output_file.close()
        if self.toconsole:
            print(thestring)
        if self.std_logging:
            logging.info(thestring)

        
            

    def dictprint(self, intro, dictionary, format1='s', format2='s', units='', valueconstant=None):
        self.write(':'+intro+':\t')
        for key in dictionary:
            value=dictionary[key]
            if valueconstant:
                value=value*valueconstant
            self.write('\t:'+('%'+format1)%key+': '+('%'+format2)%value+' '+units)
        self.write('')

    def info(self, intro, value):
        message=':'+intro+':\t'+value
        self.write(message+'\n')

    def message(self, messagestring):
        self.write(messagestring+'\n')
        
    def listprint(self, intro, thelist, format1='s', units=''):
        self.write(':'+intro+':\t')
        for value in thelist:
            self.write('\t:'+('%'+format1)%value+' '+units)
        self.write('')
            
    def plots_created(self, plot_intro, listofplots):
        underline=underline_string(plot_intro, punctuation='.')
        self.write(underline)
        self.write(plot_intro)
        self.write(underline+'\n')
        for plot in listofplots:
            self.write(plot+'\n')
            self.write('.. image::\t'+plot+'\n')
            
    def header(self, name, punctuation='-'):
        underline=underline_string(name, punctuation=punctuation)
        self.write(underline)
        self.write(name)
        self.write(underline+'\n')


def underline_string(mystring, punctuation='='):
    length=len(mystring)

    return punctuation*length



def sphinx_files(logfile, imagepattern, tablepattern, ms_name, 
                 sphinx_path, quasar_number, make_html=None, user_flagging_script=None):
    """
    Copy the .rst logfile, any images matching the specified pattern,
    any tables matching the specified pattern into a directory named
    after the ms, and located in the sphinx path

    """

    #get the path for the number of quasars
    quasar_dir=str(int(quasar_number))+'quasar'
        
    #get the name of direcotry to store results for this measurement
    #set, and create it if it doesn't already exist
    resultsdir = os.path.join(sphinx_path, quasar_dir, ms_name+'_resultsdir')
    if not os.path.isdir(resultsdir):
        os.mkdir(resultsdir)

    #copy files into that directory
    shutil.copy(logfile, resultsdir)
    print resultsdir

    for thefile in os.listdir('.'):
        if imagepattern:
            if fnmatch.fnmatch(thefile, imagepattern):
                shutil.copy(thefile, resultsdir)
        if tablepattern:
            if fnmatch.fnmatch(thefile, tablepattern):
                shutil.copy(thefile, resultsdir)

    if user_flagging_script:
        shutil.copy(user_flagging_script, resultsdir)
        

                
    #make html in sphinx:
    #first remove casapy from environ
    try:
        oldpythonpath=os.environ['PYTHONPATH']
    except KeyError:
        oldpythonpath=''
    newpythonpath=[]
    for i in oldpythonpath[:].split(':'):
        if i.find('casa') == -1:
            newpythonpath.append(i)
    os.environ['PYTHONPATH']=':'.join(newpythonpath)

    oldpath=os.environ['PATH']
    newpath=[]
    for i in oldpath[:].split(':'):
        if i.find('casa') == -1:
            newpath.append(i)

    #remove 2 spurious entries...
    newpath.pop(0)
    newpath.pop(0)
    os.environ['PATH']=':'.join(newpath)
    cwd=os.getcwd()
    os.chdir(sphinx_path)

    if make_html:
        ret=subprocess.call('make html', shell=True)
        if ret !=0:
            print 'Could not make sphinx html automatically'
    os.environ['PYTHONPATH']=oldpythonpath
    os.environ['PATH']=oldpath
    os.chdir(cwd)

        
def cleanup_files(pattern):
     for thefile in os.listdir('.'):
        if fnmatch.fnmatch(thefile, pattern):
            if os.path.isdir(thefile):
                try:
                    shutil.rmtree(thefile)
                except OSError:
                    print 'Could not remove '+thefile
            elif os.path.isfile(thefile) and not fnmatch.fnmatch(thefile, '*.fits'):
                try:
                    os.remove(thefile)
                except OSError:
                    print 'Could not remove '+thefile
                

def get_restoring_beam(images, logging=None):
    """
    Get the beam size from the image headers.
    prints the beammajor, beamminor and beampa to log.

    """
    if not logging:
        mylog=mylogger(output_file=None, console=True)
    else:
        mylog=logging

    mylog.header('Beam Info from images')
    beams={}
    for image in images:
        imlist=imhead(imagename=image, mode='list')
        field=imlist['object']
        beammajor=imlist['beammajor']
        beamminor=imlist['beamminor']
        beampa=imlist['beampa']
        beamdict={'Major':beammajor, 'Minor':beamminor,'PA':beampa}
        mylog.dictprint(image,beamdict)
        beams[field]=beamdict
    return beams
        
    
def write_out_csv_file(csv_list, csv_name):
    """
    Write out a list of rows as a csv file to csv_name
    """

    csvfile=open(csv_name, 'w')
    writer=csv.writer(csvfile)

    for row in csv_list:
        writer.writerow(row)

    csvfile.close()



def make_postage_plot(fitsfile, slices, imsize, pixsize, imagename, 
                      figsize=[4,12], slicenames=['I','Q','U','V']):
    """
    Make a small plot of the centre of a fits file.

    Seems to work for most quasar plots?

    """
    try:
        import aplpy
        import aplpy.chanmap

        #get pixsize as float..
        
        pixsize=float(str(pixsize).split('arcsec')[0])
    
        
        gc=aplpy.chanmap.GridImages(fitsfile, slices=slices, figsize=figsize, 
                                    cbar_mode='none', nrows_ncols=[1,4])
        ra, dec=gc.FITSFigure[0].pixel2world(imsize/2,imsize/2)
        gc.recenter(ra, dec, radius=pixsize*75/(60.0*60.0))
        for i in gc.FITSFigure:
            i.show_colorscale(cmap='gist_gray', pmax=99.97, stretch='arcsinh')
        gc.set_label_mode('none')
        gc.label_channels(names=slicenames, color='blue', fontsize='xx-large', 
                          va='top', ha='right')
        gc._figure.savefig(imagename)
        os.system('/usr/bin/convert -trim '+imagename+' '+imagename)
        return imagename
    except ImportError:
        print "Can't produce images of data: correct version of aplpy not existant"
        print "Try adding /data/sfg30/soft_aplpydev/lib/python2.6/site-packages/"
        print "To the front of the pythonpath"
        return None
        
