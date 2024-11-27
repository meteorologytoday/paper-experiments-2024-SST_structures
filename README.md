# paper-experiments-2024-SST_structures

## Directory `01_sounding`


## Directory `02_sounding`

## Directory `03_modified_WRF_code`

This directory contains files that are used to modify the setup of WRF idealized runs. Specifically, I modify the setup of the idealize case `em_quarter_ss`. Here I list what is done in each file.

- `module_initialize_ideal.F`
    1. Changing the the land grid to water grid so that the roughness height will be water's value. See L.314-323, L.362-363. The modification works by checking the roughness length and land type in output files. 
    2. Remove the initial hard-coded perturbation by adding in `If (.false.) THEN ... END` between L.1119-1165.
    3. Set the Coriolis parameter `grid%f` to `1.e04` throughout the domain at L.399.
    4. Remove the initial hard-coded perturbation by adding in `If (.false.) THEN ... END` between L.1119-1165.


