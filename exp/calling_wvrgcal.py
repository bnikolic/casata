# Sarah Graves <s.graves@mrao.cam.ac.uk>
# Initial version October 2011

""" 
A program for calling wvrgcal from within casapy (or python).
"""

import subprocess
import numpy as np
import casata.tools
from casata.tools import extprog
import sys
import inspect



try:
    from taskinit import casalog
    casa_env=True
except ImportError:
    print 'Not in a casa aware environment, cannot use casalog.'
    casa_env=None
    pass
    



class wvrgcal(object):
    """A class for using a system WVRGCAL binary

    Once initialised, this class will check the binary can be called
    successfully with --help and access the version number of the
    binary being used. The wvrgcal command can then be accessed
    through wvrgcal.call(**kwargs).

    Example usage:
    >>> from calling_wvrgcal import wvrgcal
    >>> #first initialise the setup
    >>> mywvrgcal=wvrgcal('/home/sfg30/softwvr/bin/wvrgcal', usecasalog=True)
    >>> mywvrgcal.call(ms='MyMeasurementset.ms', output='MyOutputTable.W')

    The commandline options can be accessed by running:
    >>> mywvrgcal.call(help=True) 

    This will print the optional parameters to screen, unfortunately in
    the GNU format. When calling from this setup, these must be used
    in the keyword=Value, rather than as '--keyword Value'.

    To use keyword options that do not take a value, set the value to be true.

    i.e., to run wvrgcal --help, use:
    >>> mywvrgcal.call(help=True)

    The version number can be accessed as:
    >>> mywvrgcal.version
    """

    def __init__(self, path=None, usecasalog=True):
        """
        Initialise the chosen wvrgcal binary.

        path: |None | str|

             This gives the path to the chosen wvrgcal binary
             (including the name wvrgcal,
             i.e. '/installdir/bin/wvrgcal' If set to None (the
             default) it will use the available system path to call
             'wvrgcal'

        usecasalog: |True |False| 

             If in a casa environment (i.e. within a casapy terminal)
             this willl allow wvrgcal to write to the casalog and
             register errors there. 

        example usage:
        >>> from calling_wvrgcal import wvrgcal
        >>> mywvrgcal=wvrgcal(path='/path/to/bin/wvrgcal', usecasalog=True)
        >>> mywvrgcal.call(ms='MyMeasurementSet.ms', output='MyOutput.W')
        
        The version number of the chosen wvrgcal binary is written to
        screen, and can be accessed as:
        >>> mywvrgcal.version

        and the help message listing the available options for this
        version can be printed to screen via:
        >>> mywvrgcal.call(help=True)
        
        """
        if usecasalog is True and casa_env is True:
            self.casalog=True
        else:
            self.casalog=None
        
        #get version
        if path is not None:
            self.wvrgcal=path
        else:
            self.wvrgcal='wvrgcal'

        process=subprocess.Popen([self.wvrgcal, '--help'], shell=False, 
                           stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.returncode=process.wait()

        if self.returncode == 0:
            mystdin, mystderr=process.communicate()
            if mystderr is not '':
                print mystderr

            self.version=_get_wvrgcal_version(mystdin)

            print 'WVRGCAl Version: '+self.version

            if self.casalog:
                casalog.origin('wvrgcal')
                casalog.post(message=
                             'Initialised WVRGCAL version: '+self.version, 
                             origin='__init__', priority='info')
                
        else:
            mystdin, mystderr=process.communicate()
            print(mystderr)
            print('could not run the following wvrgcal call: '
                  +self.wvrgcal+' --help')
            print self.returncode

            if self.casalog:
                casalog.origin('wvrgcal')
                casalog.post(message='Could not initialise WVRGCAL!', 
                             priority='ERROR', origin='__init__')
                casalog.post(message='system call was: '+self.wvrgcal+' --help',
                             priority='ERROR', origin='__init__')
            raise Exception


    def call(self, *args, **kwargs):
        """Call the wvrgcal binary defined in __init__, with
        appropriate values Returns the error code, and prints the
        output of stdout, followed by stderr, to screen

        e.g.:
        >>> mywvrgcal.call( ms='MyMeasurementSet.ms', output='MyOutput.W')
        
        To see a full listing of available options for this version of
        wvrgcal (unfortunately in GNU format rather than python
        keyword format), please run: 
        
        >>> mywvrgcal.call( help=True)
        """

        ## section of code from casata/tools/extrprog/wvrgcal
        if len(args) > 0:
            kwargs["ms"]=args[0]
        if len(args) > 1:
            kwargs["output"]=args[1]
        if len(args) > 2:
            raise "This program can only understand 2 positional parameters"
        ### end of code copied from casata/tools/extprog/wvrgcal

        if self.casalog:
            casalog.origin('wvrgcal')
            casalog.post(message='####################################',
                         origin='call', priority='INFO')
            casalog.post(message='####  Begin WVRGCAL call', origin='call',
                          priority='INFO')
            casalog.post(message='      wvrgcal version: '+self.version, 
                         origin='call', priority='1')
            message='      wvrgcal call is: '+self.wvrgcal

            for key, val in kwargs.items():
                keystr=' --'+str(key)
                if val is not True:
                    valstr='='+str(val)
                elif val is False:
                    keystr=''
                    valstr=''
                else:
                    valstr=''
                message+=keystr+valstr
            casalog.post(message=message, origin='call', priority='INFO')

        # run wvrgcal using casata.tools.extprog.call
        self.returncode=casata.tools.extprog.call(
            *self.wvrgcal.split(), **kwargs)
        
        # write to the casalog
        if self.returncode != 0:
            if self.casalog:
                casalog.origin('wvrgcal')
                casalog.post(message='Could not run WVRGCAL succesfully',
                             origin='call', priority='ERROR')
                casalog.post(message='return code was '+str(self.returncode),
                             origin='call', priority='ERROR')
                casalog.post(message='#### End WVRGCAL call', origin='call',
                             priority='INFO')

            print 'could not run following wvrgcal call: '+self.wvrgcal,kwargs
            print self.returncode
            raise OSError(
                'Please check the wvrgcal options or the wvrgcal binary')

        else:
            if self.casalog:
                casalog.post(message='#### End WVRGCAL call', origin='call',
                             priority='INFO')
            

def _get_wvrgcal_version(helpstring):
    """Gets the version number (as string) of the wvrgcal being run.
    
    Takes in the result of 'wvrgcal --help' as its only argument.  

    Note that the method used here to find the version number could
    break if the format of the output from 'wvrgcal --help' dramatically
    changes."""

    #find the line beginning with WVRGCAL
    splithelp=helpstring.split('\n')
    indices=[line.find('WVRGCAL') for line in splithelp]
    index=np.where(np.asarray(indices) != -1)[0].item()
    theline=splithelp[index]

    #get version number as part after the word 'Version'
    version=theline.split('Version')[1].strip()
    
    #return the version number
    return version
    
    


