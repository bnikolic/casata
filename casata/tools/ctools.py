# 2010 Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
#
# This file is part of casata and is licensed under GPL version 2
"""
Tools for handling CASA "tools" (that is I guess what you get for
building layers upon layers!)
"""

import os

import casac

# Map from usual short names to the "homes"
_toolMap= {"im" : "imagerHome",
           "cb" : "calibraterHome",
           "qa" : "quantaHome"
           }

def get(name):
    """
    Return a guranteed unused CASA tool whose state we can change

    For the time being just create a new one each time, but can re-use
    existing tools if this becomes limiting
    """
    t=casac.homefinder.find_home_by_name(_toolMap[name]).create()
    return t

def isMS(pname,
         msin):
    """
    Check if a measurement set exists
    """
    if not os.access(msin, 
                     os.F_OK):
        raise "Could not find measurement set"+msin


def backcompPar(pname,
                val):
    """
    This checker is used for parameters which are retained for
    compatibility only
    """
    print ("Parameter %s is retained for backward compatibility only, please do not use" % pname)
    

# Map from parameter names to their descriptions and functions to
# verify them
_stdParVer={"vis": ("Visibility set (=measurement set?) to operate on",
                    [isMS, ]),
            "selectdata" : ("",
                            [backcompPar,])
            }

def addPosArgs(args, expect,
               kwargs):
    """
    Add positional arguments to the keyword parameters dictionary
    """
    if len(args) > len(expect):
        raise "Too many positional arguments, was expecting " + str(expect)
    for a, e in zip(args, expect):
        if e in kwargs.keys():
            raise "Positional argument clashes with keyword"
        else:
            kwargs[e]=a

def checkArgs(kwargs):
    """
    Check arguments with standard names using their checker functions
    """
    for k in kwargs:
        if k in _stdParVer.keys():
            doc, cl=_stdParVer[k]
            for c in cl:
                c(k, kwargs[k])

def applyWTrans(f,
                kwargs,
                keep,
                translate):
    """
    Apply function to arguments, throwing away non-applicable ones and
    translating the names 
    """
    na={}
    for k in kwargs.keys():
        if k in translate.keys():
            na[translate[k]]=kwargs[k]
        elif k in keep:
            na[k]=kwargs[k]
    return f(**na)
    

def gencal(*args,
            **kwargs):
    """
    (a replacement for the gencal task)
    """
    addPosArgs(args, 
               ["vis", "caltable"],
               kwargs)
    checkArgs(kwargs)
    cb=get("cb")
    cb.open(kwargs["vis"])
    kwargs.pop("vis")
    cb.specifycal(**kwargs)    
    cb.close()
    

# List of parameters which are taken by the cb.selectvis
# function. 
_cbSelectvisPars = ["time",
                    "spw",
                    "scan",
                    "field",
                    "baseline",
                    "uvrange"
                    "msselect"]

_cbSetsolvePars = ["type",
                   "t",
                   "combine",
                   "preavg",
                   "refant",
                   "minblperant",
                   "solnorm",
                   "minsnr",
                   "table",
                   "apmode",
                   "phaseonly",
                   "append"]

_cbSetsolvegainsplinePars = ["table",
                             "append",
                             "mode",
                             "refant",
                             "splinetime",
                             "preavg",
                             "npointaver",
                             "phasewrap"]


def gaincal(*args,
             **kwargs):
    """
    (a replacement for the gaincal task)
    """
    # Translation from the parameters to the gaincal task to actual
    # parameters to selectvis function of cb tool
    _cbSelectvisPars_translate= {"timerange": 
                                 "time"}
    # As above but for the setsolve function
    _cbSetsolvePars_translate= { "solint" : "t",
                                 "caltable" : "table",
                                 "calmode" : "apmode"}
    # As above but for the cb.setsolvegainspline function
    _cbSetsolvegainsplinePars_translate = { "caltable" : "table",
                                            "calmode" : "mode"}
    
    addPosArgs(args, 
               ["vis", "caltable"],
               kwargs)
    checkArgs(kwargs)    
    cb=get("cb")
    cb.open(kwargs["vis"])
    kwargs.pop("vis")
    applyWTrans(cb.selectvis,
                kwargs,
                _cbSelectvisPars,
                _cbSelectvisPars_translate)

    # Pre-calibration apply
    spwmap=kwargs.get("spwmap", [])
    interp=kwargs.get("interp", [])
    gainfield=kwargs.get("gainfield", [])
    for i, g in enumerate(kwargs.get("gaintable", [])):
        if i >= len(spwmap):
            cspw=[-1]
        else:
            cspw=spwmap[i]
        if i >= len(interp):
            cinterp="linear"
        else:
            cinterp=interp[i]            
        if i >= len(gainfield):
            cgainfield=""
        else:
            cgainfield=gainfield[i]            
        cb.setapply(t=0.0,
                    table=g,
                    field=cgainfield,
                    calwt=True,
                    spwmap=cspw,
                    interp=cinterp)

    phaseonly=False
    gaintype=kwargs.pop("gaintype")
    if (gaintype=='G'):
        kwargs["type"]="G"
        kwargs["phaseonly"]=phaseonly
        applyWTrans(cb.setsolve,
                    kwargs,
                    _cbSetsolvePars,
                    _cbSetsolvePars_translate)
    elif (gaintype=='T'):
        kwargs["type"]="T"
        kwargs["phaseonly"]=phaseonly
        applyWTrans(cb.setsolve,
                    kwargs,
                    _cbSetsolvePars,
                    _cbSetsolvePars_translate)
    elif (gaintype=='GSPLINE'):
        applyWTrans(cb.setsolvegainspline,
                    kwargs,
                    _cbSetsolvegainsplinePars,
                    _cbSetsolvegainsplinePars_translate)
                    
    cb.solve()            
    cb.close()    
