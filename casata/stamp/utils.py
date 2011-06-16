# 2011 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
import os

def dataselname(msin,
                **kwargs):
    pref,junk=os.path.splitext(os.path.basename(msin))
    res=pref
    for k in kwargs.keys():
        if kwargs[k] != None:
            res+="%s-%s-" % (k, str(kwargs[k]))
    return res


