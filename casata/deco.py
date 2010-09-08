# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Top level function decorators and support functions
"""

def casaGlobD(f):
    """
    Decorator for functions that are broken because they depend on
    global CASA objects and functions
    """
    def rf(*pars, **kwargs):
        print "Function %s only works if defined at top level scope" % f.func_name
        return f(*pars, 
                  **kwargs)
    rf.func_name=f.func_name
    rf.func_doc=f.func_doc
    return rf

def logPars(f):
    """
    Decorator that illustrates how to log parameters to a function, if
    one wanted to do so....
    """
    def rf(*pars, **kwargs):
        print "Positional arguments" , pars
        print "Keyword arguments" , kwargs
        return f(*pars, 
                  **kwargs)
    rf.func_name=f.func_name
    rf.func_doc=f.func_doc
    return rf
