#!/bin/bash

rm -f log.run

echo "Running ideal.exe"
./ideal.exe 2>&1 >> log.run

echo "Modifying SST"
mv wrfinput_d01 wrfinput_d01.backup
python3 modify_init_sine.py 2>&1 >> log.run

#mpirun -np 2 wrf.exe
echo "Running WRF"
./wrf.exe 2>&1 >> log.run
