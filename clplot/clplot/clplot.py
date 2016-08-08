"""
Closure phase plotting
"""

import matplotlib
import matplotlib.pylab as plt
if matplotlib.__version__ > '1.4.0':
     plt.style.use('ggplot')


#import pandas as pd

def phaseSpec(d):
    if type(d) == list:
        for x in d:
            plt.plot(x[0,:,0])
    else:
        plt.plot(d[0,:,0])
    plt.ylabel("Closure phase (rad)")    
    plt.xlabel("Channel #")

def ampSpec(d):
    plt.plot(d[0,:,0])
    plt.ylabel("Closure amplitude")    
    plt.xlabel("Channel #")    


def phaseTime(d):
    for i in range(d.shape[1]):
        plt.plot(d[0,i,:])
    plt.ylabel("Closure phase (rad)")            
    plt.xlabel("Time slot")

def ampTime(d):
    for i in range(d.shape[1]):
        plt.plot(d[0,i,:])
    plt.ylabel("Closure amplitude")            
    plt.xlabel("Time slot")    

def phaseM(d, nside=3):
    plt.figure(dpi=75)
    for t in range(min(len(d["tr"]), nside**2)):
        plt.subplot(nside, nside, t+1)
        #phaseSpec(d["phase"][t])
        phaseTime(d["phase"][t])        
        plt.title("triad-%i-%i-%i" % tuple(d["tr"][t]))
    
             

