import numpy as np
from scipy import interpolate

def getGridFromGridDensity(sigma, sigma_density, new_grid_number, reverse=False):

    N = len(sigma)
    gn = np.zeros((N,))

    sigma = np.array(sigma)
    sigma_density = np.array(sigma_density)

    if reverse is True:
        sigma         = sigma[::-1]
        sigma_density = sigma_density[::-1]


    if np.any(sigma[1:] - sigma[:-1] <= 0):
        raise Exception("sigma array is not monotinically increasing. Please check both the array content and reverse option.")

    if np.any(sigma_density <=0):
        raise Exception("sigma_density should be positive.")

    for i in range(1, N):
        gn[i] = gn[i-1] + (sigma_density[i] + sigma_density[i-1]) * (sigma[i] - sigma[i-1]) / 2

    norm_factor = (new_grid_number-1) / gn[-1]

    gn = gn * norm_factor

    grids = np.interp(
        np.arange(new_grid_number),
        gn,
        sigma,
    )

    if reverse is True:
        gn = gn[::-1]
        sigma = sigma[::-1]
        grids = grids[::-1]


    return grids, gn, norm_factor

"""
# This is the default WRF layers.
# I only put them here for the purpose of comparison.
WRF_default_sigma = np.array([1, 0.9339951, 0.8719891, 0.81374, 0.7590199, 0.7076152, 0.659325, 0.6139605, 0.5713445, 0.5313104, 0.493702, 0.458372, 0.4251827, 0.3940042, 0.3647146, 0.3371996, 0.3113517, 0.2870699, 0.2642592, 0.2428305, 0.2227001, 0.2037894, 0.1860244, 0.1693357, 0.1536582, 0.1389305, 0.1250951, 0.112098, 0.09988828, 0.08841833, 0.07764333, 0.06752115, 0.05801222, 0.04907943, 0.04068783, 0.03280466, 0.02539911, 0.01844224, 0.01190686, 0.005767446, 0 ])

WRF_default_dsigma = WRF_default_sigma[:-1] - WRF_default_sigma[1:]

kappa = 2.0 / 7.0
WRF_default_Pi = WRF_default_sigma ** kappa
WRF_default_dPi = WRF_default_Pi[:-1] - WRF_default_Pi[1:]
"""

def genGridDensity(N, den1=50, den2=200, sig_mixed_layer = 0.75, transition_thickness=0.25, reverse=False):

    sigma = np.linspace(0, 1, N)
    sigma_density = sigma.copy()


    p1 = sig_mixed_layer - transition_thickness
    p2 = sig_mixed_layer


    blend = den1 + (den2 - den1) * (sigma - p1) / (p2 - p1)

    sigma_density[sigma <  p1 ] = den1

    trans_idx = (sigma >= p1) & (sigma < p2)
    sigma_density[trans_idx] =  blend[trans_idx]
    sigma_density[sigma >= p2] = den2
    
    if reverse:
        sigma = sigma[::-1]
        sigma_density = sigma_density[::-1]


    return sigma, sigma_density

#sigma_hires, sigma_density = genGridDensity(1001, reverse=True, den1=50, den2=50)
sigma_hires, sigma_density = genGridDensity(1001, reverse=True)
sigma, gn_hires, norm_factor = getGridFromGridDensity(sigma_hires, sigma_density, 101, reverse=True) 

output_str = ", ".join(["%.04f" % c for c in sigma])


with open("grid.txt", "w") as f:
    f.write(output_str)


print("Output coordinate string:")
print(output_str)


import matplotlib as mplt
mplt.use("TkAgg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, squeeze=False, sharey=True)

ax[0, 0].plot(sigma_density * norm_factor, sigma_hires, "k-")
ax[0, 1].plot(gn_hires,      sigma_hires, "k-")

ax[0, 0].set_ylabel("Sigma")
ax[0, 0].invert_yaxis()

ax[0, 0].set_xlabel("Density")
ax[0, 1].set_xlabel("Numbering")

ax[0, 0].set_title("(a) Relative grid density $\\mathrm{d}N/\\mathrm{d}\\sigma$")
ax[0, 1].set_title("(b) Grid Numbering")


ax[0, 0].set_xlim([0, None])

for _ax in ax.flatten():
    _ax.grid()

fig.savefig("grid_design.png", dpi=200)

plt.show()
