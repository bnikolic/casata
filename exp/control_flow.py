#Sarah Graves 2011


from quasar_functions import *
from casata.tools.vtasks import *
import numpy as np
import calling_wvrgcal
import logging
import time
import datetime

__version__='0.1'

#exec(os.popen("bzr version-info --format=python").read())
#__version__='%(revno)'%version_info

def quasar_reduction(vis, spws=[1,3,5,7], user_flagging_script=None,
                     control='complete', wvrgcal_options=None, antpos_corr=None, 
                     cal_field=0, ref_ant='DV02', logfile=None, n_iter=100, 
                     make_html=None, clean_files=None, 
                     sphinx_path='/data/sfg30/WVR/quasar_runs/',
                     group='almawvr'):

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
    starttime_s=time.time()
    starttime_clock=datetime.datetime.now()
    timestamp=starttime_clock.strftime('%Y-%m-%d_%H-%M-%S')

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
            

    #ms names
    root_name = os.path.split( os.path.splitext(vis.rstrip('/'))[0] )[1]
    print root_name
    file_root = root_name #base name of file
    #now include timestamp in basic name
    root_name=root_name+timestamp
    split1=root_name+'_split1.ms'
    split2=root_name+'_cont.ms'
    #imfit and stats .csv files
    imfit_csv_name=root_name+'_imfit.csv'
    stats_csv_name=root_name+'_stats.csv'
    stats_csv_name_short=root_name+'_stats_short.csv'
    imfit_csv_name_short=root_name+'_imfit_short.csv'

    #setup the logfile
    if not logfile:
        logfile=root_name+'.rst'

    mylog=mylogger(root_name=root_name, output_file=True, console=True, logfile=logfile)
    #set up toc to be correct depth
    mylog.message(':tocdepth: 3'+'\n')
    #intial title of page
    if do_wvrgcal:
        mywvrgcal=calling_wvrgcal.wvrgcal(wvrgcal)
        ver=mywvrgcal.version
        wvrhead='WVRGCAL ver. '+ver+' wvroptions:'
        wvr_string='WVR: '+ver
        mystr=''
        for key in wvrgcal_options:
            mystr+=key+'='+str(wvrgcal_options[key])+' '
        wvrhead+=' '+mystr
        wvr_opt_string=mystr
    else:
        wvrhead='No WVRGCAL'
        wvr_string=''
        wvr_opt_string=''
        

    runtitle=file_root+' '+timestamp+' '+wvrhead+' control: '+str(control)
    if user_flagging:
        runtitle+=' '+user_flagging

    mylog.header(runtitle, punctuation='#')
    mylog.header('quasar_reduction is being performed', punctuation='=')
    optdict=dict(vis=vis, spws=[1,3,5,7], user_flagging_script=user_flagging_script,
                   control=control, wvrgcal_options=wvrgcal_options, 
                   antpos_corr=antpos_corr, 
                   cal_field=cal_field, ref_ant=ref_ant, logfile=logfile, n_iter=n_iter)

    quasar_reduction_version=__version__
    quasar_reduction_opt_string=''
    for key in optdict:
        quasar_reduction_opt_string+=key+'='+str(optdict[key])+' '
        
    mylog.dictprint('Options called', optdict)
    mylog.info('Reduction began at', starttime_clock.strftime('%c'))
    mylog.info('root name for files', root_name)

    #always do: setup names, parameters and get basic info
    #get basic info from data set
    #TODO: SEPARATE THIS INTO SEPARATE FUNCTIONS!
    mylog.header('Basic Info', punctuation='-')
    antennas, field_dict, spw_chandict, spw_freqdict, band, max_baseline=get_vis_info(vis,
                     spws, logging=mylog)

    
    
    #TODO: GET THIS FROM VIS
    correlations=['XX','YY']
    mylog.info('Manually set correlations are', str(correlations))
    
    #setup names and parameters -- leave it here rather than in
    #various functions so if we need to improve in future its easy to
    #do. 
    #TODO: THINK ABOUT FILE NAMES



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
    mask_dx=20

    #list of unapplied calibration tables
    unapplied_caltables=[]


    #TODO: should copy data over?
    if initial_calibrations:

        mylog.header('Initial flagging and calibrations', punctuation='=')
        #initial calibrations
        if antpos_corr:
            caltable_name=antenna_position_correct(vis, antpos_corr,
                                                   antpos_caltable, logging=mylog)
            unapplied_caltables.append(caltable_name)

        #if wvrgcal chosen,
        if do_wvrgcal:
            
            caltable_name, wvrversion = call_wvrgcal(vis, wvrgcal_table,
                                                     wvrgcal, 
                                                     field_dict, cal_field,
                                                     antennas, logging=mylog,
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
        apriori_flagging(split1, logging=mylog)

        flagging_spw_ends(split1, spw_chandict, band, logging=mylog)

        #plots of data
        inital_plot_names=initial_plots(split1, spw_chandict.keys(), correlations, 
                                        root_name, logging=mylog)

    #ensure correct spws used even if not running whole thing
    spw_chandict=post_split_spw_chandict
    unapplied_caltables=[]
    #if requested, do user chosen flagging commands
    if user_flagging:

        mylog.header('USER FLAGGING', punctuation='=')

        #copy over the user_flagigng file, give it timestamped new name
        new_user_flagging_script=root_name+'_userflagging.py'
        shutil.copy(user_flagging_script, new_user_flagging_script)
        user_flagging_script=new_user_flagging_script

        execfile(new_user_flagging_script)

        mylog.message('User supplied flagging was carried out')
        mylog.info('User flagging script stored', 
                   os.path.abspath(user_flagging_script))
        mylog.message('.. literalinclude:: '
                      +user_flagging_script )

        #plots after apriori and user flagging???
        #after_apu_flagging_plots(myvis, **info_dict)
          
    if calibration:

        mylog.header('CALIBRATION', punctuation='=')
                
        #correct phases of bandpass calibrator
        bpp_caltable=bpp_calibration(split1, bpp_caltable, spw_chandict, 
                                     field_dict[cal_field], ref_ant,
                                     logging=mylog)
        #unapplied_caltables.append(bpp_caltable)
        caltable_plot(bpp_caltable, spw_chandict, root_name,  phase=True, snr=True,
                      logging=mylog)

        #bandpass calibration
        bp_caltable=bandpass_calibration(split1, bpp_caltable, bp_caltable,
                                         field_dict[cal_field], ref_ant, logging=mylog)
        #reset unapplied caltables! DON'T WANT TO APPLY THE BPP CALTABLE AFTER THIS!
        unapplied_caltables=[]
        unapplied_caltables.append(bp_caltable)

        caltable_plot(bp_caltable, spw_chandict, root_name, xaxis='chan', phase=True,
                      amp=True, snr=True, logging=mylog)

        #gain calibration
        gc_caltable, gc_amp_caltable=gain_calibration(split1, unapplied_caltables[:], 
                                             gc_caltable, gc_amp_caltable,
                                             field_dict[cal_field],
                                             ref_ant, logging=mylog)
        unapplied_caltables.append(gc_caltable)
        unapplied_caltables.append(gc_amp_caltable)
        caltable_plot(gc_caltable, spw_chandict, root_name, phase=True, snr=True, 
                      logging=mylog)
        caltable_plot(gc_amp_caltable, spw_chandict, root_name, phase=True, amp=True,
                      snr=True, logging=mylog, phase_range=[])

        #apply calibrations, slightly differently for cal_field and regular
        apply_calibrations_calsep(split1, unapplied_caltables, field_dict, cal_field, logging=mylog)

        #plot corrected data
        
        corrected_plots(split1, spw_chandict, field_dict,  correlations, root_name, 
                        logging=mylog)

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
        mylog.header('IMAGING', punctuation='=')
        #freq=np.mean(spw_freqdict.values())
        #pixsize, im_size=get_imaging_params(freq, max_baseline)
        #bx, mask = make_box_and_mask(im_size, mask_dx)

        #clean data (i.e. make images)
        #TODO: test this function
        imagenames=clean_data(split2, pixsize, im_size, mask, n_iter, field_dict,
                              cleanweighting, cleanspw, cleanmode, root_name, logging=mylog)
        
        #make fits images:
        fitsimages=create_fits_images(imagenames, logging=mylog)

        #make picture of fitsfiles:
        for fitsfile in fitsimages:
            print fitsfile
            finalpicname=fitsfile+'.'+figext
            finalpicname=make_postage_plot(fitsfile, [[0,0],[1,0],[2,0],[3,0]],
                                       im_size, pixsize, finalpicname)
            if finalpicname:
                mylog.plots_created('', [finalpicname])
            
    if stats:
        #compute stats                
        stats_csv=stats_images(imagenames, bx, logging=mylog)
        imfit_csv=imfit_images(imagenames, mask, logging=mylog)
        beams=get_restoring_beam(imagenames, logging=mylog)

        #write out short stats csv file
        write_out_csv_file(stats_csv, stats_csv_name_short)
        write_out_csv_file(imfit_csv, imfit_csv_name_short)
        
        #add on full information to stats tables
        stats_csv=add_full_run_information_to_table(stats_csv, file_root, 
                            wvr_string, wvr_opt_string,
                 quasar_reduction_version, quasar_reduction_opt_string, beams=beams)
        imfit_csv=add_full_run_information_to_table(imfit_csv, file_root, 
                     wvr_string, wvr_opt_string, 
                 quasar_reduction_version, quasar_reduction_opt_string, beams=beams)
        
        #write out full stats tables
        write_out_csv_file(stats_csv, stats_csv_name)
        write_out_csv_file(imfit_csv, imfit_csv_name)

        #now add  logfile
        mylog.header('STATS of Images')
        mylog.message('')
        mylog.message('The full table is stored in '+stats_csv_name)
        mylog.message('')
        mylog.write('.. csv-table:: STATS')
        mylog.write('    :header-rows: 1')
        mylog.write('    :file: '+stats_csv_name_short)
        mylog.message('')
        mylog.message('The full table is in '+imfit_csv_name)
        mylog.message('')
        mylog.write('.. csv-table:: IMFIT on STOKES I')
        mylog.write('    :header-rows: 1')
        mylog.write('    :file: '+imfit_csv_name_short)
        mylog.message('')
    
    finishtime_s=time.time()
    finishtime_clock=time.ctime()
    mylog.info('Finished at', finishtime_clock)
    mylog.info('Took', '%.1F'%((finishtime_s-starttime_s)/60.0)+' minutes')


    quasar_number=len(field_dict.keys())
    imagepattern=root_name+'*'+figext
    tablepattern=root_name+'*.csv'

    if mylog.output_file:
        sphinx_files(mylog.output_file, imagepattern, tablepattern, file_root,
                     sphinx_path, quasar_number, make_html=make_html, 
                     user_flagging_script=user_flagging_script, group=group)

    #TODO: delete files -- need to keep track of what has been created
    #so it can be deleted...  don't want to delete too much while its
    #running, to allow us to go back to extra flagging stage and run
    #stuff...
    if clean_files:
        cleanup_files(root_name+'*')
    
    
    

    

 
