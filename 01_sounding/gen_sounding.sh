#!/bin/bash

script_dir=$( dirname $( realpath $0 ) )

if [ "$1" = "" ]; then

    echo "Error: First argument must be given (geostrophic wind U)"
    exit 1

fi


SST_base=288.15 # 15 degC
RH=0
U=$1
deltaGamma=3e-3
z_st=10000.0

fileprefix=sounding_U${U}

data_dir=sounding_files
fig_dir=sounding_plot


mkdir -p $data_dir
mkdir -p $fig_dir

python3 $script_dir/make_ideal_sounding_simple.py \
    --output $data_dir/${fileprefix}.ref \
    --Delta-Gamma $deltaGamma \
    --U $U   \
    --RH $RH \
    --T-sfc $SST_base  \
    --z-st  $z_st \
    --output-fig $fig_dir/${fileprefix}.png \
    --no-display

