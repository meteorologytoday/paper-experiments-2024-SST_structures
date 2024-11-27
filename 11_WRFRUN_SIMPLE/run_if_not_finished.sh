#!/bin/bash

#trap 'kill $( jobs -p )' EXIT

lab_dir=./lab_SIMPLE

target_file=wrfout_d01_2001-01-19_18:00:00
for run_dir in $( ls $lab_dir ) ; do


    full_run_dir=$lab_dir/$run_dir

    
    if ! [[ "$run_dir" =~ "MYNN25" ]]; then
        echo "Skip $run_dir"
        continue
    fi

    if ! [[ "$run_dir" =~ "dT100" ]]; then
        echo "Skip $run_dir"
        continue
    fi




    # Test if wrfout is there

    cwd=`pwd`
    if [ -f "$full_run_dir/$target_file" ]; then
        x=x
        #echo "Target file detected in $run_dir . Skip."

    else
        echo "Submitting the case: $run_dir" 
        cd $full_run_dir
        sbatch --time 72:00:00 submit_cw3e-shared.sh
        #sbatch submit_cw3e-compute.sh
    fi
    cd $cwd
done

