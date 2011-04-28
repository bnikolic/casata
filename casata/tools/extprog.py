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
         *pargs,
         **kwargs):
    """
    Call progname converting kwargs into standard gnu syntax
    """
    args=[progname]
    args.extend(pargs)
    for k in kwargs.keys():
        if kwargs[k] is False:
            # If options is false assume it is skipped completely
            continue
        if kwargs[k] is True:
            # If paremeter is exactly "True" then it is an option only
            args.append("--%s" %k)
        elif type(kwargs[k]) in  [list, tuple]:
            for v in kwargs[k]:
                args.append("--%s" %k)
                args.append(str(v))
        else:
            args.append("--%s" %k)
            args.append(str(kwargs[k]))
    r=subprocess.call(args)
    if r != 0:
        print "Warning: external program returned error status -- inspect the output"
    return r


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
    cmdline=kwargs.pop("cmdline", "wvrgcal")
    call(*cmdline.split(), 
         **kwargs)
        


    

