import numpy as np
import xarray as xr
import json

input_filename = "wrfinput_d01.backup"
output_filename = "wrfinput_d01"
setting_filename = "run_setting.json"


ds = xr.open_dataset(input_filename, engine='netcdf4')

_, Ny, Nx = ds.TSK.shape

with open(setting_filename, "r") as f:
    setting = json.load(f)

T0  = setting['T0']
dT  = setting['dT']
wnm = setting['wnm']

YC = ds.DY * ( np.arange(Ny) + 0.5 )
XC = ds.DX * ( np.arange(Nx) + 0.5 )

LX = ds.DX * Nx

TSK = T0 + dT * np.sin(2 * np.pi * XC * wnm / LX)
for j in range(Ny):
    ds.TSK[0, j, :] = TSK
    ds.SST[0, j, :] = TSK
    ds.TMN[0, j, :] = TSK

ds['F'][:] = setting['f0']
ds['E'][:] = 0

print("Output file : ", output_filename)
ds.to_netcdf(output_filename)
