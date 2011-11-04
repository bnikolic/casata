# Bojan Nikolic 
# Initial version November 2011
"""
Functional data analysis, test script
"""

@Macro
def AntPos(ms, aname, apos):
    return None

@Macro
def MyPos(ms):
    ms=AntPos(ms, "DV01", [0, -1 , 2])
    ms=AntPos(ms, "DV02", [1, 2, 3])
    return ms


    


