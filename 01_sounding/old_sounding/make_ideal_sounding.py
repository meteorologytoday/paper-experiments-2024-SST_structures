import pandas as pd
import numpy as np
import argparse

from WRFSoundingTools import writeWRFSounding 

parser = argparse.ArgumentParser(description='This program generate idealized sounding profile. Below the inversion layer the potential temperature is well-mixed. Above the inversion layer user can choose how stable the atmosphere has to be.')
parser.add_argument('--output', type=str, help='Output sounding filename.', required=True)

parser.add_argument('--theta-sfc',    type=float, help='Surface potential temperature.', default=288.15)
parser.add_argument('--dthetadz-mix', type=float, help='Stratification within mixed-layer', default=0.0)
parser.add_argument('--p-sfc',       type=float, help='Surface temperature in hPa.', default=1000.0)
parser.add_argument('--H-mix',     type=float, help='Height of mixed layer.', default=1500.0)
parser.add_argument('--H-tpp',     type=float, help='Height of inversion layer.', default=10e3)
parser.add_argument('--RH-mix',    type=float, help='Relative humidity (%) in the mixed layer.', default=0)
parser.add_argument('--RH-ft',     type=float, help='Relative humidity (%) in the free troposphere.', default=0)
parser.add_argument('--RH-st',     type=float, help='Relative humidity (%) in the stratosphere.', default=0)
parser.add_argument('--Delta-Gamma-ft', type=float, help='Relative humidity (%) in the free troposphere.', default=0)
parser.add_argument('--U', type=float, help='Wind in the x-direction.', default=0.0)
parser.add_argument('--V', type=float, help='Wind in the y-direction', default=0.0)

parser.add_argument('--no-display', action="store_true")
parser.add_argument('--output-fig', type=str, help='Output figure filename.', default="")

parser.add_argument('--total-height', type=float, help='Total atmospheric height (m).', default=23e3)
parser.add_argument('--Nz', type=float, help='Number of points.', default=500)

args = parser.parse_args()


for arg, val in vars(args).items():
    print("{:15} : {}".format(arg, val))



latent_heat = 2.5e6
theta0 = 300.0
g0     = 9.81
c_p     = 1004.0
R      = 287.0
kappa = R / c_p
p_ref  = 1e5
M_H2O = 0.018
M_DRY = 0.02896
R_uni = 8.3145
def p2Pi(p):
    return (p / p_ref)**kappa

def saturation_vapor_pressure(T):
    T_degC = T - 273.15 
    return 6.112 * np.exp(17.67 * T_degC / (T_degC + 243.5)) * 100.0

def getMixingRatio(T, p, RH):
    p_wv = saturation_vapor_pressure(T) * RH

    return p_wv / (p - p_wv) * M_H2O / M_DRY

def getPotentialTemperature(T, p):

    return T * (p_ref / p)**kappa 
    
def getEquivalentPotentialTemperature(T, p, RH):

    es = saturation_vapor_pressure(T)
    rho_wv = es * RH * M_DRY / (R_uni * T)
    dtheta = rho_wv * latent_heat / c_p
 
    return getPotentialTemperature(T, p) + dtheta 



# N**2 = g0/theta0 dtheta/dz

print("theta0 = %f" % (theta0,))
print("g0 = %f" % (g0,))
print("c_p = %f" % (c_p,))


z_W = np.linspace(0.0, args.total_height, args.Nz+1)

theta = z_W.copy()
T     = z_W.copy()
RH    = z_W.copy()
Pi    = z_W.copy()

Gamma_ft = g0 / c_p - args.Delta_Gamma_ft


Pi_sfc  = p2Pi(args.p_sfc * 1e2)

theta_Hm = args.theta_sfc + args.H_mix * args.dthetadz_mix

if args.dthetadz_mix == 0:
    dPi_Hm = - g0 / c_p / args.theta_sfc * args.H_mix
else:
    dPi_Hm = - g0 / c_p / args.dthetadz_mix * np.log( 1 + args.dthetadz_mix / args.theta_sfc * args.H_mix )
    
Pi_Hm   = Pi_sfc + dPi_Hm
T_Hm = Pi_Hm * theta_Hm

Pi_Htpp = Pi_Hm * ( 1 - Gamma_ft * (args.H_tpp - args.H_mix) / T_Hm ) ** (g0 / Gamma_ft / c_p)
T_Htpp = T_Hm - Gamma_ft * (args.H_tpp - args.H_mix) 

for i, z in enumerate(z_W):

    if z <= args.H_mix:
        theta[i] = args.theta_sfc + args.dthetadz_mix * z

        if args.dthetadz_mix == 0:
            dPi = - g0 / c_p / args.theta_sfc * z
        else:
            dPi = - g0 / c_p / args.dthetadz_mix * np.log( 1 + args.dthetadz_mix / args.theta_sfc * z )
         
        Pi[i]    = Pi_sfc + dPi
        T[i]     = theta[i] * Pi[i]

        RH[i]    = args.RH_mix / 1e2


    elif z <= args.H_tpp:
        T[i] = T_Hm - Gamma_ft * ( z - args.H_mix )
        Pi[i] = Pi_Hm * ( 1 - Gamma_ft * (z - args.H_mix) / T_Hm) ** (g0 / Gamma_ft / c_p)
        theta[i] = T[i] / Pi[i]

        RH[i] = args.RH_ft / 1e2
         
    else:
        T[i] = T_Htpp
        Pi[i] = Pi_Htpp * np.exp( - g0 * (z - args.H_tpp) / c_p / T_Htpp )
        theta[i] = T[i] / Pi[i]

        RH[i] = args.RH_st / 1e2



p_W = Pi**(1/kappa) * p_ref
T_W = T
theta_e = getEquivalentPotentialTemperature(T, p_W, RH)


w_W = z_W.copy()
u_W = z_W.copy()
v_W = z_W.copy()

u_W[:] = args.U
v_W[:] = args.V

# Humidity

w_W = getMixingRatio(T_W, p_W, RH) * 1e3

df_sfc = pd.DataFrame.from_dict(dict(
    air_pressure = [args.p_sfc], # output in [hPa]
    potential_temperature = [args.theta_sfc],
    mixing_ratio = [w_W[0]],
))


# Omit the surface layer
df_sdg = pd.DataFrame.from_dict(dict(
    height = z_W[1:],
    potential_temperature = theta[1:],
    mixing_ratio = w_W[1:],
    wind_x = u_W[1:],
    wind_y = v_W[1:],
))

print("Output sounding: %s" % (args.output,))
writeWRFSounding(args.output, df_sfc, df_sdg)




print("Loading matplotlib...")
import matplotlib
if args.no_display:
    matplotlib.use('Agg')
else:
    matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
print("Done")

import matplotlib.transforms as transforms




fig, ax = plt.subplots(1, 3, sharey=True)

offset = 273.15
ax[0].plot(T - offset, z_W, label="$T$")
ax[0].plot(theta - offset, z_W, label="$\\theta$")
ax[0].plot(theta_e - offset, z_W, label="$\\theta_e$")

ax[1].plot(RH, z_W, label="RH")
ax[1].twiny().plot(w_W, z_W, label="mixing ratio")

ax[2].plot(u_W, z_W, label="$U$")
ax[2].plot(v_W, z_W, label="$V$")


for _ax in ax.flatten():
    _ax.legend()
    _ax.grid()

    trans = transforms.blended_transform_factory(_ax.transAxes, _ax.transData)
    _ax.plot([0, 1], [args.H_mix]*2, linestyle='--', color="red", transform=trans)
    _ax.plot([0, 1], [args.H_tpp]*2, linestyle='--', color="red", transform=trans)

ax[0].set_xlim([-30, 100])
ax[1].set_xlim([-0.05, 1.05])
ax[2].set_xlim([-20, 20])

ax[0].set_ylim([0, 8000])

if args.output_fig != "":
    print("Saving output figure: ", args.output_fig)
    fig.savefig(args.output_fig, dpi=300)

if not args.no_display:
    print("Showing figure...")
    plt.show()

