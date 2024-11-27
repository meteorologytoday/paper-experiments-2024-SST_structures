import numpy as np


def gaussian(x, xc, sigma):
    
    return np.exp( - ( (x - xc) / sigma )**2 / 2 )

def SST_shape(X, XC, dT, wid, spacing, wpkt):
    
    TSK = np.zeros((len(XC),)

    for i in range(wpkt):
    
        cent = XC + i * spacing

        TSK += dT * gaussian(X, cent, wid);

    return TSK
