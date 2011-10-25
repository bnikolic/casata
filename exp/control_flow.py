

def quasar_reduction(vis, *args, **kwargs, user_flagging_script=None,
                   control='complete'):
    
    #control flow of quasar script
    if control=='complete':
         initial_calibrations=True
         calibration_and_imaging=True
         user_flagging=user_flagging_script
    if control=='initial':
        initial_calibrations=True
        calibration_and_imaging=None
        user_flagging=user_flagging_script
    if control=='final':
        initial_calibrations=None
        calibration_and_imaging=True
        user_flagging = user_flagging_script

    #always do: setup names, parameters and get basic info
    #get basic info from data set
    info=get_quasar_info(vis, **kwargs?)

    #setup names and parameters -- leave it here so if we need to
    #improve in future its easy to do
    #....  
    #....


    if initial_calibrations:
        #initial calibrations
        antenna_position_correct(*args, **kwargs)

        #if wvrgcal chosen,
        if do_wvrgcal:
            call_wvrgcal(wvrgcal_options)

        #apply cal
        if unapplied_caltable:
            applycal(**kwargs)

        #split out science spws (1,3,5 and 7? always?)
        #should be choice to script, to allow for quick-look, 
        #single spw reduction
        split(*args, **kwargs)

       
        #apriori flagging
        #should this include flagging beginning and end 10% of chans?
        apriori_flagging(vis, **apriori_options)

        #plots of data
        initial_plots(myvis, **info_dict)

        

    #if requested, do user chosen flagging commands
    if user_flagging:
        execfile(user_flagging_script)
        #plots after apriori and user flagging
        after_apu_flagging_plots(myvis, **info_dict)
          
    if calibration_and_imaging:
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

        #box for computing image statistics within:
        #TODO: less hardcoded!
        bx, mask = make_box_and_mask(im_size, mask_dx)

        #clean data (i.e. make images)
        #TODO: test this function
        imagenames=clean_data(split2, pixsize, im_size, mask, n_iter, field_dict,
                              cleanweighting, cleanspw, cleanmode)

        #make fits images:
        fitsimages=create_fits_images(imagenames)

        #compute stats        
        #TODO: these functions are made but not tested...
        stats_images(imagenames, bx, logfile=mylogfile)
        imfit_images(imagenames, mask, logfile=mylogfile)
    
    
    
    
    

    

    
