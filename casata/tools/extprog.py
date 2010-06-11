# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
# Initial version March 2010
#
# Part of the WVR phase correction software suite libAIR
"""
Convenient bindings in Python to external program with the standard
option syntax
"""

import subprocess

def call(progname,
         **kwargs):
    """
    Call progname converting kwargs into standard gnu syntax
    """
    args=[progname]
    for k in kwargs.keys():
        args.append("--%s" %k)
        if kwargs[k] is True:
            # If paremeter is exactly "True" then it is an option only
            pass
        else:
            args.append(str(kwargs[k]))
    subprocess.call(args)


def wvrgcal(*args,
             **kwargs):
    """
    Call the wvrgcal program 
    """
    if len(args)>0:
        kwargs["ms"]=args[0]
    if len(args)>1:
        kwargs["output"]=args[1]
    if len(args)>2:
        raise "This program can only understand two positional parameters"
    call("wvrgcal", 
         **kwargs)
        


    

