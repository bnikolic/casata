#Sarah Graves 2011


from quasar_functions import *
from casata.tools.vtasks import *
import numpy as np
import calling_wvrgcal

def quasar_reduction(vis, spws=[1,3,5,7], user_flagging_script=None,
                   control='complete', wvrgcal_options=None, antpos_corr=None, 
                     cal_field=0, ref_ant='DV02'):

    """
    Function to reduce 4 (and 1?) quasar data sets

    arguments:
    *vis*: the measurement set to run on, *string*

    *spws*: science spws to examine (i.e. usually [1,3,5,7]), *list* (or array?)
    
    *user_flagging_script*: the name (and path if not in cwd) of a
     user provided script, which will contain additional casa flagging commands.

    TODO: this will only be able to run commands that are in casata.tools.vtasks...

    *control*: ['complete' | 'initial' | 'final'  | 'imaging' | 'stats' ]

    string defining which sections of script will run.

    *wvrgcal_options*: options for wvrgcal

    TODO: think about best way to include this?

    antpos_corrections:
    Define additional arguments here as I add them in. 

    
    
    """
    
    #control flow of quasar script
    if control=='complete':
         initial_calibrations=True
         calibration=True
         imaging=True
         stats=True
         user_flagging=user_flagging_script
    
    elif control=='initial':
        initial_calibrations=True
        calibration=None
        imaging=None
        stats=None
        user_flagging=user_flagging_script
    
    elif control=='final':
        initial_calibrations=None
        calibration=True
        imaging=True
        stats=True
        user_flagging = user_flagging_script
    
    elif control=='imaging':
        initial_calibrations=None
        calibration=None
        user_flagging=None
        imaging=True
        stats=True
    
    elif control=='stats':
        initial_calibrations=None
        calibration=None
        user_flagging=None
        imaging=None
        stats=True
    

    #wvrgcal setup; run if options are defined (or if wvrgcal_options
    #set to True...)
    if wvrgcal_options:
        do_wvrgcal=True
        try:
            wvrgcal=wvrgcal_options.pop('wvrgcal')
        except KeyError:
            wvrgcal='wvrgcal'
    else:
        do_wvrgcal=None
            

    #always do: setup names, parameters and get basic info
    #get basic info from data set
    #TODO: SEPARATE THIS INTO SEPARATE FUNCTIONS!
    antennas, field_dict, spw_chandict, spw_freqdict, band, max_baseline=get_vis_info(vis, spws)

    #TODO: GET THIS FROM VIS
    correlations=['XX','YY']
    
    #setup names and parameters -- leave it here rather than in
    #various functions so if we need to improve in future its easy to
    #do. 
    #TODO: THINK ABOUT FILE NAMES

    #ms names
    root_name = os.path.split( os.path.splitext(vis)[0] )[1]
    split1=root_name+'_split1.ms'
    split2=root_name+'_cont.ms'

    #spw channel dictionary after splitting out the spws of interest:
    post_split_spws=range(0,len(spws))
    post_split_spw_chandict={}
    for new,old in zip(post_split_spws, spws):
        post_split_spw_chandict[new]=spw_chandict[old]

    #wvrgcal names
    wvrgcal_table=root_name+'_wvrgcal.W'
    
    #antenna position correction
    antpos_caltable = root_name+'_antposfix' 

    #caltable names
    bpp_caltable=root_name+'_bpphase.gcal'
    bp_caltable=root_name+'_bandpass.gcal'
    gc_caltable=root_name+'_gainphase.gcal'
    gc_amp_caltable=root_name+'_gainamp.gcal'
    #plotting parameters
    figext='png'


    #imaging parameters
    cleanmode='mfs'
    cleanweighting='briggs'
    cleanspw='' #NOTE THAT SPW HERE AND AFTER SPLIT HAVE DIFF NAMES

    #TODO: CALCULATE THIS AUTOMATICALLY!
    mask_dx=18
    n_iter=100
    #list of unapplied calibration tables
    unapplied_caltables=[]


    #TODO: should copy data over?
    if initial_calibrations:
        #initial calibrations
        if antpos_corr:
            caltable_name=antenna_position_correct(vis, antpos_corr,
                                                   antpos_caltable)
            unapplied_caltables.append(caltable_name)

        #if wvrgcal chosen,
        if do_wvrgcal:
            
            caltable_name, wvrversion = call_wvrgcal(vis, wvrgcal_table,
                                                     wvrgcal, 
                                                     field_dict, cal_field,
                                                     antennas,
                                                     **wvrgcal_options)
            unapplied_caltables.append(caltable_name)

        #apply cal
        if unapplied_caltables:
            applycal(vis=vis, gaintable=unapplied_caltables)
            unapplied_caltables=[]
            splitdatacolumn='corrected'
        else:
            splitdatacolumn='data'

        #split out science spws 
        #should be choice to script, to allow for quick-look, 
        #single spw reduction
        split(vis=vis, outputvis=split1, datacolumn=splitdatacolumn, 
              spw=string_creator(spws)
              )
        spw_chandict=post_split_spw_chandict
       
        #apriori  and beginning/end channel flagging
        apriori_flagging(split1)

        flagging_spw_ends(split1, spw_chandict, band)

        #plots of data
        inital_plot_names=initial_plots(split1, spw_chandict.keys(), correlations, 
                                        root_name)

    #ensure correct spws used even if not running whole thing
    spw_chandict=post_split_spw_chandict
    unapplied_caltables=[]
    #if requested, do user chosen flagging commands
    if user_flagging:
        execfile(user_flagging_script)

        #plots after apriori and user flagging???
        #after_apu_flagging_plots(myvis, **info_dict)
          
    if calibration:
        #correct phases of bandpass calibrator
        bpp_caltable=bpp_calibration(split1, bpp_caltable, spw_chandict, 
                                     field_dict[cal_field], ref_ant)
        #unapplied_caltables.append(bpp_caltable)
        caltable_plot(bpp_caltable, spw_chandict, root_name,  phase=True, snr=True)

        #bandpass calibration
        bp_caltable=bandpass_calibration(split1, bpp_caltable, bp_caltable,
                                         field_dict[cal_field], ref_ant)
        #reset unapplied caltables! DON'T WANT TO APPLY THE BPP CALTABLE AFTER THIS!
        unapplied_caltables=[]
        unapplied_caltables.append(bp_caltable)

        caltable_plot(bp_caltable, spw_chandict, root_name, xaxis='chan', phase=True,
                      amp=True, snr=True)

        #gain calibration
        gc_caltable, gc_amp_caltable=gain_calibration(split1, unapplied_caltables[:], 
                                             gc_caltable, gc_amp_caltable,
                                             field_dict[cal_field],
                                             ref_ant)
        unapplied_caltables.append(gc_caltable)
        unapplied_caltables.append(gc_amp_caltable)
        caltable_plot(gc_caltable, spw_chandict, root_name, phase=True, snr=True)
        caltable_plot(gc_amp_caltable, spw_chandict, root_name, phase=True, amp=True,
                      snr=True)

        #apply calibrations, slightly differently for cal_field and regular
        apply_calibrations_calsep(split1, unapplied_caltables, field_dict, cal_field)

        #plot corrected data
        corrected_plots(split1, spw_chandict, field_dict,  correlations, root_name)

        #split out corrected data, averaging all channels in each spw
        #No need to make a function wrapper to do this?
        #TODO: fix widht for case where spws don't all ahve same number of channels
        split(vis=split1, outputvis=split2, datacolumn='corrected',
          width=int(np.mean(spw_chandict.values())))

    #box for computing image statistics within:
    #TODO: less hardcoded!

    freq=np.mean(spw_freqdict.values())
    pixsize, im_size=get_imaging_params(freq, max_baseline)
    pixsize = '%.2F'%pixsize+'arcsec'
    bx, mask = make_box_and_mask(im_size, mask_dx)

    if imaging:
        #box for computing image statistics within:
        #TODO: less hardcoded!

        #freq=np.mean(spw_freqdict.values())
        #pixsize, im_size=get_imaging_params(freq, max_baseline)
        #bx, mask = make_box_and_mask(im_size, mask_dx)

        #clean data (i.e. make images)
        #TODO: test this function
        imagenames=clean_data(split2, pixsize, im_size, mask, n_iter, field_dict,
                              cleanweighting, cleanspw, cleanmode, root_name)

        #make fits images:
        fitsimages=create_fits_images(imagenames)

    if stats:
        #compute stats                
        stats_images(imagenames, bx, logfile=None)
        imfit_images(imagenames, mask, logfile=None)
    
    
    #TODO: delete files -- need to keep track of what has been created
    #so it can be deleted...  don't want to delete too much while its
    #running, to allow us to go back to extra flagging stage and run
    #stuff...
    
    
    

    

    
