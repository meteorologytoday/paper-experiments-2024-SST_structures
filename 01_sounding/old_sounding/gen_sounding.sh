#!/bin/bash

SST_base=288.15 # 15 degC
RH=90
U=15
deltaGammaFt=3e-3
H_mix=1500.0
H_tpp=10000.0

fig_dir=figure_sounding_profiles

mkdir -p $fig_dir


python3 make_ideal_sounding.py --output input_sounding_wML.ref --Delta-Gamma-ft $deltaGammaFt --U $U --H-mix $H_mix --RH-mix $RH --RH-ft $RH --theta-sfc $SST_base --output-fig $fig_dir/input_sounding_wML.png --no-display 

python3 make_ideal_sounding.py --output input_sounding_woML.ref --Delta-Gamma-ft $deltaGammaFt --U $U --H-mix $H_mix --RH-mix $RH --RH-ft $RH --theta-sfc $SST_base --dthetadz-mix 3e-3 --output-fig $fig_dir/input_sounding_woML.png --no-display

python3 make_ideal_sounding.py --output input_sounding_woML_U5.ref --Delta-Gamma-ft $deltaGammaFt --U 5.0 --H-mix $H_mix --RH-mix $RH --RH-ft $RH --theta-sfc $SST_base --dthetadz-mix 3e-3 --output-fig $fig_dir/input_sounding_woML_U5.png --no-display



# N = 5-3 s^-1 in the mixed layer
python3 make_ideal_sounding.py --output input_sounding_wMLweakstrat.ref --Delta-Gamma-ft $deltaGammaFt --U $U --H-mix $H_mix --RH-mix $RH --RH-ft $RH --theta-sfc $SST_base --dthetadz-mix .75e-3 --output-fig $fig_dir/input_sounding_wMLweakstrat.png --no-display
