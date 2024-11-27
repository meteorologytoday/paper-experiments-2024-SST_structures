import numpy as np
import xarray as xr
import json

def gaussian(x, xc, sigma):
    
    return np.exp( - ( (x - xc) / sigma )**2 / 2 )

def SST_shape(XC, begin_X, dT, wid, spacing, wpkt):
    
    TSK = np.zeros( (len(XC),) )

    for i in range(wpkt):
    
        cent = begin_X + i * spacing

        TSK += dT * gaussian(XC, cent, wid);

    return TSK



input_filename = "wrfinput_d01.backup"
output_filename = "wrfinput_d01"
setting_filename = "run_setting.json"


ds = xr.open_dataset(input_filename, engine='scipy')

ds.LU_INDEX[:, :, :] = 16


_, Ny, Nx = ds.TSK.shape

with open(setting_filename, "r") as f:
    setting = json.load(f)

T0 = setting['T0']
dT = setting['dT']
wid = setting['wid']
begin_X = setting['begin_X']
wpkt   = setting['wpkt']

YC = ds.DY * ( np.arange(Ny) + 0.5 )
XC = ds.DX * ( np.arange(Nx) + 0.5 )

TSK = T0 + SST_shape(XC, begin_X, dT, wid, 4*wid, wpkt)
for j in range(Ny):
    ds.TSK[0, j, :] = TSK

ds['F'][:] = setting['f0']
ds['E'][:] = 0


print("Output file : ", output_filename)
ds.to_netcdf(output_filename)
