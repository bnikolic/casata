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
        f(*pars, 
           **kwargs)
    return rf
