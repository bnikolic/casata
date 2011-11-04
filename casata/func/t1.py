# Bojan Nikolic 
# Initial version November 2011
"""
Functional data analysis, test script
"""

if 0:
    sys.path.remove("/usr/lib/python2.6/dist-packages/tables")

@Macro
def AntPos(ms, aname, apos):
    return None

@Macro
def MyPos(ms):
    ms=AntPos(ms, "DV01", [0, -1 , 2])
    ms=AntPos(ms, "DV02", [1, 2, 3])
    return ms


    


