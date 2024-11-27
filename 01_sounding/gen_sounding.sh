#!/bin/bash

SST_base=288.15 # 15 degC
RH=90
U=15
deltaGamma=3e-3
z_st=10000.0

fileprefix=sounding_U${U}

data_dir=sounding_files
fig_dir=sounding_plot


mkdir -p $data_dir
mkdir -p $fig_dir

python3 make_ideal_sounding_simple.py \
    --output $data_dir/${fileprefix}.ref \
    --Delta-Gamma $deltaGamma \
    --U $U   \
    --RH $RH \
    --T-sfc $SST_base  \
    --z-st  $z_st \
    --output-fig $fig_dir/${fileprefix}.png \
    --no-display

