# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Restricted Macro-like functionality for Python 
"""

def Macro(f):
    """ 
    Try to simulate non-evaluation of arguments. Do not expand the
    function.
    """
    def rf(*pars, **kwargs):
        return [f.func_name] + list(pars) + [kwargs]
    rf.expand=lambda *pars, **kwargs: f(*pars, **kwargs)
    return rf

def MacroExpand(l):
    fname=l[0]
    pars=l[1:-1]
    kwargs=l[-1]
    ll=globals()[fname]
    return ll.expand(*pars, **kwargs)

