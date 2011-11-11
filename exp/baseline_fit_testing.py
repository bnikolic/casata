#Sarah Graves Nov 2011

from quasar_functions import *
from casata.tools.vtasks import *
import numpy as np
import calling_wvrgcal
import logging
import time
import datetime
import baselinexample
import quasar_functions


def baseline_testing(vis, spw='0'):

    """
    To test the baseline fitting:



    5) baseline fitting *

    6) apply antenna position corrections from baseline fitting *

    7) split out new data with corrected positiosn *

    8) try baseline fitting again *

    """
    print 'baselinefitting'
    print 'vis='+vis

    #get antenna corrections
    print 'get antenna corrections'
    ants, corr_positions=baselinexample.baselineExample(vis, spw=spw)
    os.system('rm -rf test.G')

    #generate antenna correction tables
    print 'generate antenna correction tables'
    gencal(vis=vis, caltable='antpos_base.cal', caltype='antpos',
           antenna=','.join(ants), parameter=list(corr_positions))
    gencal(vis=vis, caltable='antpos_minus1.cal', caltype='antpos',
           antenna=','.join(ants), parameter=list(np.asarray(corr_positions)*-1.0))

    #apply base ant corr table
    print 'base ant corr table'
    split(vis=vis, outputvis='basetest.ms', datacolumn='data')
    applycal(vis='basetest.ms', gaintable='antpos_base.cal')
    split(vis='basetest.ms', outputvis='basetest_corr.ms', 
          datacolumn='corrected')
    
    #apply minus 1 * ant cor
    print 'minus1 ant corr table'
    split(vis=vis, outputvis='minus1test.ms', datacolumn='data')
    applycal(vis='minus1test.ms', gaintable='antpos_minus1.cal')
    split(vis='minus1test.ms', outputvis='minus1test_corr.ms', 
          datacolumn='corrected')

    #check output values
    print 'check residual ant corr values'
    ants, base_residual=baselinexample.baselineExample('basetest_corr.ms', spw=spw)
    os.system('rm -rf test.G')
    ants, minus1_residual=baselinexample.baselineExample('minus1test_corr.ms', spw=spw)
    os.system('rm -rf test.G')
    
    return corr_positions, base_residual, minus1_residual

                                               
    


#vis='uid___A002_X219601_X4cd.ms'

#corr_pos, base_resid, minus1_resid=baseline_testing(vis)
