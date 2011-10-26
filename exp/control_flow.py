#Sarah Graves 2011


from quasar_functions import *
from casata.tools.vtasks import *

def quasar_reduction(vis, spws=[1,3,5,7], user_flagging_script=None,
                   control='complete', wvrgcal_options=None, antpos_corrections=None):

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
    if control=='initial':
        initial_calibrations=True
        calibration=None
        imaging=None
        stats=None
        user_flagging=user_flagging_script
    if control=='final':
        initial_calibrations=None
        calibration=True
        imaging=True
        stats=True
        user_flagging = user_flagging_script

    if control=='imaging':
        initial_calibrations=None
        calibration=None
        user_flagging=None
        imaging=True
        stats=True
    if control=='stats':
        initial_calibrations=None
        calibration=None
        user_flagging=None
        imaging=None
        stats=True

    if wvrgcal_options:
        do_wvrgcal=True

    #always do: setup names, parameters and get basic info
    #get basic info from data set
    antennas, field_dict, spw_chandict, spw_freqdict, band, max_baseline=get_quasar_info(vis, spws)

    
    #setup names and parameters -- leave it here rather than in
    #various functions so if we need to improve in future its easy to
    #do. 

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
    antpos_caltable = root_name+'antpos_fix' 


    #flagging parameters
    quackinterval=1.5
    quackincrement=True
    #TODO: flagging ends of array -- this WILL NEED TO BE BAND BASED? MAYBE
    #NOT DEFINED HERE?
    spwflagrange=10
    spwflagmethod='percent'

    #plotting parameters
    figext='png'

    #list of unapplied calibration tables
    unapplied_caltable=[]

    if initial_calibrations:
        #initial calibrations
        if antpos_corrections:
            caltable_name=antenna_position_correct(vis, antenna_position_corrections,
                                                   antpos_caltable)
            unapplied_caltable.append(caltable_name)

        #if wvrgcal chosen,
        if do_wvrgcal:
            caltable_name=call_wvrgcal(wvrgcal_options)

        #apply cal
        if unapplied_caltable:
            applycal(**kwargs)

        #split out science spws (1,3,5 and 7? always?)
        #should be choice to script, to allow for quick-look, 
        #single spw reduction
        split(vis=vis, outputvis=split1, datacolumn='corrected', 
              spw=string_creator(spws))

       
        #apriori flagging
        #should this include flagging beginning and end 10% of chans?
        apriori_flagging(vis,)

        flagging_spw_ends(vis, spw_chandict)

        #plots of data
        initial_plots(myvis, **info_dict)

        

    #if requested, do user chosen flagging commands
    if user_flagging:
        execfile(user_flagging_script)
        #plots after apriori and user flagging
        #after_apu_flagging_plots(myvis, **info_dict)
          
    if calibration:
        #correct phases of bandpass calibrator
        #inf vs int...
        unapplied_caltable=bcpp_calibration_and_plots(myvis, **caloptions_dict)

        #bandpass calibration
        unapplied_caltable=bandpass_calibration(myvis, **bppoptions_dict)
        bandpass_calibration_plots(*args)

        #gain calibration
        unapplied_caltable, unapplied_caltable_calfield=gain_calibration(*args, **kwargs)
        gain_calibration_plots(*args)

        #apply calibrations, differently for cal_field and regular
        apply_the_calibrations(*args, **kwargs)

        #plot corrected data
        corrected_plots(*args)

        #split out corrected data, averaging all channels in each spw
        #No need to make a function wrapper to do this?
        split(vis=split1, outputvis=split2, datacolumn='corrected',
          width=spw_chandict.values())

    if imaging:
        #box for computing image statistics within:
        #TODO: less hardcoded!
        bx, mask = make_box_and_mask(im_size, mask_dx)

        #clean data (i.e. make images)
        #TODO: test this function
        imagenames=clean_data(split2, pixsize, im_size, mask, n_iter, field_dict,
                              cleanweighting, cleanspw, cleanmode)

        #make fits images:
        fitsimages=create_fits_images(imagenames)

    if stats:
        #compute stats        
        #TODO: these functions are made but not tested...
        stats_images(imagenames, bx, logfile=mylogfile)
        imfit_images(imagenames, mask, logfile=mylogfile)
    
    
    
    
    

    

    
