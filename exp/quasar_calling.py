import os
from quasar_functions import get_vis_info, showinfo
from quasar_functions import get_imaging_params, string_creator, flagging_spw_ends
import numpy as np
#from quasar_functions import apriori_flagging

import matplotlib
matplotlib.rcParams['font.size']=7

import calling_wvrgcal

#TODO: fix get_imaging_params
#TODO: what does Bojan mean about antenna correction format?
#TODO: Requires different method anyway? Should look at dates?
#TODO: Check if string creator for wvrgcal caller is required

#TODO: check what happens if you call corrected data column but
#      haven't applied corrections...

#TODO: why are we saving flag table?

#TODO: shall we just always flag first and last 10% of channels?
#      In 64 channels, this would be flag *:0~5 , *:57~64

#TODO: single quasar? skip plots of other fields, don't apply
#calibrations to other fields


#TODO: if we want to be able to reset any of the default values, just
#try to read in a parameter file (specified in function call) after
#setting the default values. Only need to specify those that have
#changed...

#TODO: Better way to read in external file containing additional
#flagging commands? CHECK NAMESPACES

#TODO: Check control flow: allow: beginning only | Full script | From
#additional flagging only (so don't have to repeat apriori
#calibrations again)

gencal_ant = 'DV02,DV04,DV05,DV06,DV07,DV08,DV10,DV12,DV13,PM01,PM03'
gencal_pos = [
     0.000228, -0.000334, -0.000013,
     0.000163, 0.000239, 0.000025,
     0.000060, -0.000092, 0.000384,
     0.000053, 0.000158, 0.000001,
     0.000103, 0.000328, 0.000351,
    -0.000039, -0.000085, -0.000041,
    -0.000331, -0.000056, 0.000246,
     0.000133, -0.000210, -0.000160,
    -0.000045, 0.000104, 0.000109,
     0.000191, 0.000010, 0.000119,
     0.000159, 0.000005, -0.000054
]

wvrgcal_options={'toffset': -1, 'segsource': True}
#                 'wvrflag':['DV08','DV10'], 'statsource': '1924-292'}

def reduce_quasar_data( vis, spws=[1,3,5,7], cal_field=0,
                        gencal_ant=None, gencal_pos=None,
                        wvrgcal=None, wvrgcal_options=None,
                        extra_flagging_file=None, beginning_only=False,
                        ref_ant=None):
    """
    Reduces and analyses ALMA Quasar data sets.
    
    Required arguments:

        *vis* [string] 
        The name of an alma visibility data set

    Keyword arguments:

        *spws*: [ List of integers ]
        List of science spws being used
        
        *cal_field*: [ *0* | integer ]
        The field to use as calibration source

        *gencal_ant*: [*None* | list of strings| comma-sep string ]
        The list of antennas to apply corrections to
        
        *gencal_pos*: [ *None* | list of floats ]

        Antenna position corrections to antennas specified in
        *gencal_ant*.  Order must be appropriate for order of
        *gencal_ant*.

        *wvrgcal*: [ *None* | path to wvrgcal binary]

        Whether or not to run wvrgcal. If not None, set to either the
        full path to the requested wvrgcal binary
        (e.g. '/software/bin/wvrgcal') or set as 'wvrgcal' and use the
        first occurence found in the system path.

        *wvrgcal_options*: [ *None* | dictionary of options ]

        Dictionary of keyword options to be passed to wvrgcal. By
        default wvrgcal will tie all sources, calculate coefficients
        seperately for each source, and use the cal_field as the only
        source to compute statistics on. To turn these off set
        wvrgcal_options={'tie': False, 'segsource': False,
        'statsource': False}.
    
        *extra_flagging_file*: [ *None* | name of file ] 

        If defined, this will read in and execute the named file,
        which is expected to contain additional casapy commands to be
        carried out after apriori and beginning/end flagging.

        
        *beginning_only*: [ *False* | True]

        If True, then only run the beginning of the script (apriori
        and spw beginning/end flagging, plots of amplitude vs channel)

        *ref_ant*: [ string ]
        
        The referance antenna

    """

    #basic names
    ms_name = vis
    root_name = os.path.split( os.path.splitext(ms_name)[0] )[1]
    root=root_name
    split1=root_name+'_split1.ms'
    split2=root_name+'_cont.ms'

    #wvrgcal names
    wvrgcal_table=root_name+'_wvrgcal.W'

    #antenna position correction
    antpos_caltable = 'antpos_fix' 
    antpos_caltype = 'antpos'  

    #flagging parameters
    quackinterval=1.5
    quackincrement=True
    
    #extra flagging
    #various methods? should be in parameters?
    spwflagrange=10
    spwflagmethod='percent'
    
    #generic parameters -- what should be keyword option?
    #interactive: decide whether to show gui or not for commands that
    #offer this
    #interactive=False
    figext='.png'

    #get information about data set
    ants, field_names, field_ids, spw_chandict, spw_freqdict,band,max_baseline=get_vis_info(myvis)

    #CHECK FOR 7 M ANTENNA -- these don't have wvr, need to be flagged
    #in WVRGCAL call -- possibly all start with CM field dictionary
    field_dict=dict( zip( field_ids, field_names) )
    im_size=512
    n_iter=100
    mask_dx=18
    pix='0.25arcsec'
    

    #list of unapplied calibration tables
    unapplied_caltable=[]

    #post split spws
    post_split_spws=range(0,len(spws))
    post_split_spw_chandict={}
    for new,old in zip(post_split_spws, spws):
        post_split_spw_chandict[new]=spw_chandict[old]
    
    #bandpass calibrator phase calibration
    bpp_caltable= root+'bpphase.gcal'
    #bandpass phase spw creator?
    bpp_cal_spw=[]
    for spw in post_split_spw_chandict:
        n_chans=post_split_spw_chandict[spw]
        bpp_cal_spw.append(str(spw)+':'
                           +str(int(round(n_chans/3)))
                           +'~'+str(int(round(n_chans/2)))
                           )
    
    bpp_cal_spw=string_creator(bpp_cal_spw)
    #TODO: FIX THIS?
    #longer solint in Band 9 to increase S/N
    if band == 9:
        bpp_cal_solint='inf'
    else:
        bpp_cal_solint='int'
    
    bpp_cal_minsnr=2.0
    bpp_cal_minblperant=4
    # bpp plot names
    bpp_cal_plot=root+'01_bpcal_phase_vs_time'
    

    #bandpass calibration
    bp_caltable=root+'bandpass.bcal'
    bp_spw=''
    bp_combine=''
    bp_solint='inf'
    bp_fillgaps=20 #interpolate across flagged channels in spw 1
    bp_minblperant=4
    bp_solnorm=True
    bp_cal_plot_phase=root+'02_bandpass_phase'
    bp_cal_plot_amp=root+'02_bandpass_amp'

    #-----Gain Calibration
    gc_caltable = root+'intphase.gcal'
    gc_caltable_scanphase=root+'scanphase.gcal'
    gc_calmode = 'p'
    gc_solint = 'int'  #One phase solution per integration.
    if band ==9:
        gc_solint='inf' #unless its band 9, which is noisier...
    
    #TODO: check for single quasar, set 3minutes ??
    gc_solint_ap='inf'
    gc_solint_scanphase= 'inf'
    gc_minsnr=2.0
    gc_minblperant=4
    gc_amp_caltable = root+'amp.gcal'
    gc_phase_plot=root+'03_phase_vs_time'
    gc_residphase_plot=root+'04_resid_phase_vs_time'
    gc_amptime_plot=root+'04_amp_vs_time'

    #applying calibrations
    #-----Applying calibrations
    cal_cal_interp = ['nearest','nearest','nearest']
    cal_sci_interp=['nearest','linear','linear']

    #remaining param            
    corrdata_plot=root+'05_corrected_amp_vs_time'
    corrdata_uvplot=root+'05_corrected_amp_vs_uvdist_f'

    resid_caltable=root+'gresid'
    resid_plot=root+'06_resid_phase_spw0_X'
    sample_ants = ['DV10', 'DV07', 'DV06']

    cleanmode='mfs'
    cleanweighting='briggs'
    cleanspw=''


    #-----------------------------------------------------
    # generating intial calibrations

    #antenna position calibrations
    if gencal_ant and gencal_pos:
        print 'ANTENNA POSITION CORRECTION --------'
        gencal( vis=ms_name, caltable=antpos_caltable,
                caltype=antpos_caltype,
                antenna=gencal_ant,
                parameter=gencal_pos)
        unapplied_caltable.append( antpos_caltable )
        
        
    #wvr corrections
    if wvrgcal:

        print 'WVRGCAL -----'
        if wvrgcal is True:
            wvrgcal='wvrgcal'

        mywvrgcal = calling_wvrgcal.wvrgcal(wvrgcal)
        #set up wvrgcal keyword options
        if not wvrgcal_options:
            wvrgcal_options={}
            
        #if statsource not set, use cal_field
        if not wvrgcal_options.has_key('statsource'):
            wvrgcal_options['statsource']=field_dict[cal_field]

        #if not specified, use segsource
        if not wvrgcal_options.has_key('segsource'):
            wvrgcal_options['segsource']=True
            
        #if 'tie' option not set, tie all fields
        if not wvrgcal_options.has_key('tie'):
            wvrgcal_options['tie']=string_creator(field_names)
        else:
            try:
                wvrgcal_options['tie']=string_creator(
                    wvrgcal_options['tie'])
            except TypeError:
                pass
                
        #run wvrgcal
        mywvrgcal.call(ms=ms_name, output=wvrgcal_table, **wvrgcal_options)
        unapplied_caltable.append( wvrgcal_table )

    
    #applycal for antenna positions and wvrgcal, if done
    if unapplied_caltable:
        print 'Applying calibrations ------'
        #applycal(vis=ms_name, gaintable=unapplied_caltable)
        unapplied_caltable=[]

    #separate only the science spws
    print 'SPLIT OUT SCIENCE DATA ----'
    split(vis=ms_name,
          outputvis = split1,
          datacolumn = 'corrected', #We have applied the antpos_fix
                                    #table (+wvr table perhaps).
          spw = string_creator(spws)
          )

    #spws are now renamed, so need correct ID's, and correct #channels
    
    
    spw_chandict=post_split_spw_chandict
    spws=post_split_spws
    
    print '---- SAVE ORIGINAL FLAG TABLE ----'
    flagmanager(vis = split1,
                mode = 'save',
                versionname = 'Original',
                comment = 'Right after split.')

    print '---- A PRIORI FLAGGING ----'
    apriori_flagging(vis=split1, quackinterval=1.5, quackincrement=True)
        
    print '---- plots of amp versus channel for each spw'
    for spw in spws:
        filename=root+'00_initial_amp_vs_chan_spw'+str(spw)+'.png'
        plotms(vis=split1, xaxis='channel', yaxis='amp', field='',
               avgtime='1e8', correlation='XX,YY',coloraxis='corr',
               plotfile=filename, overwrite=True,interactive=False)

    print '----Further flagging?----'
    spw_markers=flagging_spw_ends(spw_chandict, method=spwflagmethod,
                                 flagrange=spwflagrange)
    #TEMPTODO: repeating marcel's version
    spw_markers=['*:0~3'] 
    flagdata(vis=split1, flagbackup=False, spw=spw_markers)

    #at this point allow user to check?
    if beginning_only:
        print 'ending the script early, to allow stuff to be checked'
        return 0

    # run extra flagging commands if these have been provided (CHECK
    # NAMESPACE!
    if extra_flagging_file:
        execfile(extra_flagging_file)
        
    #band pass calibration.
    
    print '------ calibrate phases for bandpass calibrator----'
    #correct bandpass PHASE ONLY
    gaincal(vis=split1, caltable=bpp_caltable,
            field=field_dict[cal_field],
            refant=ref_ant, calmode='p', spw=bpp_cal_spw,
            minsnr=bpp_cal_minsnr, minblperant=bpp_cal_minblperant,
            solint=bpp_cal_solint)

    unapplied_caltable.append(bpp_caltable)

    print '------ PLOT PHASE VS TIME FOR BANDPASS CAL -----'
    print '      (...01_bpcal_phase_vs_time.X.png etc)'

    #seems like casa happily overwrites figures -- no need to remove
    #them?
    plotphase_args={
        'caltable': bpp_caltable, 'xaxis': 'time', 'yaxis': 'phase',
            'iteration': 'antenna', 'plotrange': [0,0,-180,180],
            'subplot': 441,'showgui': False        }
    poln='X'
    plotphase_args['poln']=poln
    plotphase_args['figfile']=bpp_cal_plot+'.'+poln+figext

    plotcal(**plotphase_args)

    poln='Y'
    plotphase_args['poln']=poln
    plotphase_args['figfile']=bpp_cal_plot+'.'+poln+figext

    plotcal(**plotphase_args)
    
    print '---- BANDPASS CALIBRATION ----'
    #bp calibrator phase correction applied on fly
    #TODO: check gain table being applied?
    bandpass(vis=split1, caltable=bp_caltable, 
             gaintable=unapplied_caltable, 
             field=field_dict[cal_field],
             spw=bp_spw, combine=bp_combine, refant=ref_ant,
             solint=bp_solint, solnorm=bp_solnorm,
             minblperant=bp_minblperant, fillgaps=bp_fillgaps)

    #the produced cal table includes the gains fro previous, so only
    #need one...
    unapplied_caltable=[bp_caltable]

    #plot bandpass calibration table for each spw
    plotbp_cal_args={
        'caltable': bp_caltable, 'xaxis': 'chan',
        'yaxis': 'phase', 'iteration': 'antenna',
        'plotrange': [0,0,-180,180],
        'subplot': 441}

    #phase vs channel
    for spw in spws:
        plotbp_cal_args['spw']=str(spw)
        plotbp_cal_args['figfile'] = bp_cal_plot_phase+'_spw'+str(spw)+figext
        plotcal(**plotbp_cal_args)

    #amplitude vs channel
    plotbp_cal_args['yaxis']='amp'
    plotbp_cal_args['plotrange']=[]
    for spw in spws:
        plotbp_cal_args['spw']=str(spw)
        plotbp_cal_args['figfile'] = bp_cal_plot_amp+'_spw'+str(spw)+figext
        plotcal(**plotbp_cal_args)
             
          
    print '---- GAIN CALIBRATION ----'
    #TODO: FIX NEEDED FOR BAND 9, INSUFFICENT S/N
    if band != 9:
        gaincal(vis=split1, field=field_dict[cal_field],
                gaintable=unapplied_caltable,
                refant=ref_ant, calmode='p', minsnr=gc_minsnr,
                minblperant=gc_minblperant,
                solint=gc_solint, caltable=gc_caltable)

        #TODO: CHECK I'M STILL APPLYING ALL THE CORRECT TABLES...,
        #either earlier the previous tables applied on the fly via
        #'gaintable'should have been applied, or here the bandpass
        #caltable should no longer need to be applied...
        unapplied_caltable_calfield=list(unapplied_caltable)
        unapplied_caltable_calfield.append(gc_caltable)
    #else:
    gaincal(vis=split1, field=field_dict[cal_field],
           gaintable=unapplied_caltable,
           refant=ref_ant, calmode='p', minsnr=gc_minsnr,
           minblperant=gc_minblperant,
           solint=gc_solint_scanphase, 
           caltable=gc_caltable_scanphase)
    if band == 9:
        unapplied_caltable_calfield=list(unapplied_caltable)
        unapplied_caltable_calfield.append(gc_caltable_scanphase)

    #always use the scanphase caltable for non-calibrator fields
    unapplied_caltable.append(gc_caltable_scanphase)

    #now do 'ap' calibration
    gaincal(vis=split1, field=field_dict[cal_field],
           gaintable=unapplied_caltable,
           refant=ref_ant, calmode='ap', minsnr=gc_minsnr,
           minblperant=gc_minblperant,
           solint=gc_solint_ap, caltable=gc_amp_caltable)

    #keep track of unapplied calibration tables...
    unapplied_caltable.append(gc_amp_caltable)
    unapplied_caltable_calfield.append(gc_amp_caltable)
    #create plots of the calibration tables...

    print '...phase cal (done differntly for band 9 than others!)'
    plot_dict={
        'xaxis': 'time', 'yaxis': 'phase',
        'field': '', 'spw': '', 'iteration': 'antenna',
        'subplot': 441, 'plotrange': [0,0,-180,180],
        'caltable': gc_caltable}

    for poln in ['X', 'Y']:
        plot_dict['poln']=poln
        plot_dict['figfile'] = gc_phase_plot+'_'+poln+figext
        plotcal(**plot_dict)
        
    print '...residual phase'
    plot_dict['caltable']=gc_amp_caltable
    plot_dict['plotrange']=[]
    plot_dict['figfile'] = gc_residphase_plot+figext
    
    plotcal(**plot_dict)
    
    print '...amp vs time X and Y'
    plot_dict['yaxis']='amp'
    
    for poln in ['X', 'Y']:
        plot_dict['poln']=poln
        plot_dict['figfile'] = gc_amptime_plot+'_'+poln+figext
        plotcal(**plot_dict)
        
    #bootstrapping would go here if there was a flux calibrator

    #apply calibration
    print '---- APPLY CALIBRATION (applycal) ----'
    print '...field '+field_dict[cal_field]
    
    #Bandpass calibrator and phase reference source.
    #TODO: why is flagbackup True?
    cfield=field_dict[cal_field]
    mygainfields = [cfield for i in unapplied_caltable]
    print 'applycal for calibration field'
    print 'gaintables: ', unapplied_caltable_calfield
    applycal(vis = split1, field = cfield,
            interp = cal_cal_interp, 
            gaintable=unapplied_caltable_calfield, 
            gainfield=mygainfields,
            flagbackup=True)
             
    #Remaining fields:
    tempfielddict=field_dict.copy()
    #remove the cal_field entry from field list
    tempfielddict.pop(cal_field)
    fieldlist=string_creator([field for field in tempfielddict.values()])
    #applycal
    print 'applycal for remaining fields'
    print 'gaintables: ', unapplied_caltable
    applycal(vis=split1, field=fieldlist, 
            interp=cal_sci_interp,
            gaintable=unapplied_caltable, gainfield=mygainfields,
            flagbackup=True)


    print '---- MAKING PLOTS OF CORRECTED DATA ----'

###PLOTMS INVESTIGATIONS##
    plotms_kwargs=dict(
        vis = split1,
        xaxis = 'time',
        yaxis = 'amp',
        ydatacolumn = 'corrected',
        coloraxis = 'field',
        avgchannel=string_creator(spw_chandict.values())

    #amplitude vs time, per spw and per correlation
    for correlation in ['XX','YY']:
        plotms_kwargs['correlation']=correlation
        for spw in spws:
            plotms_kwargs['spw']=str(spw)
            plotms_kwargs['plotfile']=corrdata_plot+'_spw'+str(spw)+'_'+correlation+figext
            plotms(**plotms_kwargs)

    #amplitude vs uvdist, one field per plot, colors spw
    plotms_kwargs['xaxis']='uvdist'
    plotms_kwargs['avgtime']='1e8'
    #number of channels -- this doesn't work if they have different
    #numbers of channels???

    #plotsms has no keyword avgchan...

    plotms_kwargs['coloraxis']='spw'
    plotms_kwargs['spw']=''
    for correlation in ['XX','YY']:
        for field in field_dict.values():
            plotms_kwargs['field']=field
            plotms_kwargs['plotfile']=corrdata_uvplot+field+'_'+correlation+figext
            plotms(**plotms_kwargs)
    
    print '--- CALCULATE RESIDUAL PHASE ERRORS ----'
    gaincal(vis=split1, field='', caltable=resid_caltable,
            gaintable=unapplied_caltable, solint='int', 
            refant=ref_ant)
    print '---plots of residual phase'
    print '...generate plots of phase vs time for 3 baselines. resid_phase_spw0_X.png.'
    plotcal_kwargs=dict(figfile=resid_plot, 
                        caltable=resid_caltable, 
                        xaxis='time',
                        yaxis='phase', markersize=2, plotrange=[], 
                        spw='0', poln='X', 
                        subplot=311)
    plotcal_kwargs['overplot']=False

    orig_marker_edgewidth=matplotlib.rcParams[
        'lines.markeredgewidth']
    matplotlib.rcParams['lines.markeredgewidth']=0.0
    for antenna, subplot in zip(sample_ants, [311,312,313]):
        plotcal_kwargs['antenna']=antenna
        plotcal_kwargs['subplot']=subplot
        plotcal_kwargs['overplot']=False
        for field, color in zip(field_dict.values(), ['red','green','blue','black']):
            plotcal_kwargs['field']=field
            plotcal_kwargs['plotcolor']=color
            plotcal(**plotcal_kwargs)
            plotcal_kwargs['overplot']=True
        ax=pl.gca()
        title=ax.get_title()
        title+=' antenna:'+antenna
        ax.set_title(title)


    fig=pl.gcf()
    fig.savefig(plotcal_kwargs['figfile'])


    print '---- SPLIT, MERGING CHANNELS ----'
    split(vis=split1, outputvis=split2, datacolumn='corrected',
          width=str(64) )
    print '---- CLEANING ----'
    x1 = im_size/2 - mask_dx/2
    x2 = im_size/2 + mask_dx/2
    y1 = im_size/2 - mask_dx/2
    y2 = im_size/2 + mask_dx/2
    clean_kwargs=dict(vis=split2, cell=pix, imsize=im_size,
                      niter = n_iter,
                      stokes = 'IQUV',
                      weighting = cleanweighting,
                      robust = 0.0,
                      spw = cleanspw,
                      mode = cleanmode,
                      mask = [x1, y1, x2, y2])

    for field in field_dict.values():
        print field
        clean_kwargs['field']=field
        clean_kwargs['imagename']=root+'f'+field
        clean(**clean_kwargs)

    print '---- IMAGES MADE, NOW COMPUTING STATS ----'

    #Area for background stats. Large rectangle in top half of image.
    bx = str(20)+','+str(int(im_size*0.625))+','+str(im_size-20)+','+str(im_size-20)

    for field in field_dict.values():
        imname = root+'f'+field+'.image'
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
        print str(obj['value'])+'\n'+'ST            MAX               MIN                RMS              OMIN       MAX/RMS\nI  '+str(gstat_I['max'][0])+'  '+ str(gstat_I['min'][0])+'  '+str(bgstat_I['rms'][0])+'  '+str(bgstat_I['min'][0])+'  '+str(gstat_I['max'][0]/bgstat_I['rms'][0])+'\n'+'Q  '+str(gstat_Q['max'][0])+'  '+str(gstat_Q['min'][0])+'  '+str(bgstat_Q['rms'][0])+'  '+str(bgstat_Q['min'][0])+'  '+str(gstat_Q['max'][0]/bgstat_Q['rms'][0])+'\n'+'U  '+str(gstat_U['max'][0])+'  '+str(gstat_U['min'][0])+'  '+str(bgstat_U['rms'][0])+'  '+str(bgstat_U['min'][0])+'  '+str(gstat_U['max'][0]/bgstat_U['rms'][0])+'\n'+'V  '+str(gstat_V['max'][0])+'  '+str(gstat_V['min'][0])+'  '+str(bgstat_V['rms'][0])+'  '+str(bgstat_V['min'][0])+'  '+str(gstat_V['max'][0]/bgstat_V['rms'][0])

    print '---- EXPORTING FITS (I,Q,U,V) IMAGES ----'

    default(exportfits)
    for field in field_dict.values():
        imname = root+'f'+field+'.image'
        exportfits(imagename=imname, fitsimage=imname+'.fits')

    print '---- RUNNING IMFIT ON STOKES I IMAGES ----'

    default(imfit)
    for field in field_dict.values():
        imname = root+'f'+field+'.image'
        print imname
        fit_vals = imfit(imname, box = str(x1)+','+str(y1)+','+str(x2)+','+str(y2), stokes = 'I')
        flx = fit_vals['results']['component0']['flux']
        shp = fit_vals['results']['component0']['shape']
        print 'Flux: ' + str(round(flx['value'][0],4))+' +/- '+str(round(flx['error'][0],5)) +'\n'+ 'Major axis FWHM: ' + str(round(shp['majoraxis']['value'],3))+' +/- '+str(round(shp['majoraxiserror']['value'],4)) +'\n'+ 'Minor axis FWHM: ' + str(round(shp['minoraxis']['value'],3))+' +/- '+str(round(shp['minoraxiserror']['value'],4)) +'\n'+ 'PA: ' + str(round(shp['positionangle']['value'],1))

    print '---- SCRIPT COMPLETED ----'


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
    flagmanager(vis=vis, mode='save', versionname='apriori',
                comment = 'After, autocorr, shadow, and quack.')


       
        
myvis='uid___A002_X219601_X4cd.ms'
reduce_quasar_data( myvis, spws=[1,3,5,7], cal_field=0,
                        gencal_ant=gencal_ant, gencal_pos=gencal_pos,
                        wvrgcal='/data/sfg30/softwvr_script/bin/wvrgcal', 
                    wvrgcal_options=wvrgcal_options,
                        extra_flagging_file=None, beginning_only=False,
                        ref_ant='DV02')
