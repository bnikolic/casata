# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Definition of computation endpoints
"""

endp=[]

def EndP(f):
    """
    Defines an end-point of computation, i.e., point where output
    (==sideffect) occurs
    """
    def rf(*pars, **kwargs):
        endp.append([f.func_name] + list(pars) + [kwargs])
    return rf

@EndP
def MSCpy(ms,
          fnameout):
    """
    Copy processed data to output dataset. Use only for interoperation
    with other software
    """
    return None



