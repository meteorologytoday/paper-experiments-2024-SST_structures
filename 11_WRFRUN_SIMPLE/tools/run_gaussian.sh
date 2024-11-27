#!/bin/bash

rm -f log.run

./ideal.exe 2>&1 >> log.run

mv wrfinput_d01 wrfinput_d01.backup
python3 modify_init_gaussian.py 2>&1 >> log.run

#mpirun -np 2 wrf.exe
wrf.exe 2>&1 >> log.run
