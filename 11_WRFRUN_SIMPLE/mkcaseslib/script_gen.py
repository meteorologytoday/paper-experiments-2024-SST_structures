


def genScript(
    jobname,
    partition,
    memory,
    test_file_for_startrun,
    test_file_for_completion,
):


    return """#!/bin/bash
#SBATCH -p {partition:s}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem={memory:s}
#SBATCH -t 24:00:00
#SBATCH -J {jobname:s}
#SBATCH -A csg102
#SBATCH -o {jobname:s}.%j.%N.out
#SBATCH -e {jobname:s}.%j.%N.err
#SBATCH --export=ALL

export SLURM_EXPORT_ENV=ALL

source /home/t2hsu/.bashrc_WRF_intel


local_scratch=/scratch/${{USER}}/job_${{SLURM_JOBID}}


echo "Local scratch    : $local_scratch"
echo "SLURM_SUBMIT_DIR : $SLURM_SUBMIT_DIR"

test_file_for_startrun={test_file_for_startrun:s}
test_file_for_completion={test_file_for_completion:s}

if ! [ -f "${{test_file_for_startrun}}" ] ; then
    echo "The startrun file ${{test_file_for_startrun}} is not found. This is the start run."
    f90nml -p -g time_control -v restart=.false. namelist.tmp > namelist.input
else
    echo "The startrun file ${{test_file_for_startrun}} is found. This is the restart run."
    f90nml -p -g time_control -v restart=.true. namelist.tmp > namelist.input
fi


echo "Copying files to local scratch"

ls | grep -v -e wrfout -e ".err" -e ".out" | xargs -I % cp % -t $local_scratch

cd $local_scratch

echo "Current directory: `pwd`"
echo "Running run_sine.sh"
bash ./run_sine.sh &
PID=$!
echo "WRF pid = $PID"

tail --retry -f --pid=$PID log.run

echo "Program finished. Copy files back..."
ls | xargs -I % cp % -t $SLURM_SUBMIT_DIR

echo "Output files copied."


cd $SLURM_SUBMIT_DIR

if [ -f "${{test_file_for_completion}}" ] ; then
    echo "The completion file ${{test_file_for_completion}} is found. No need to submit another one."
else
    echo "The completion file ${{test_file_for_completion}} is not found. Need to submit another one."
    sbatch ${{0}}
fi



""".format(
    jobname=jobname,
    partition=partition,
    memory=memory,
    test_file_for_completion=test_file_for_completion,
    test_file_for_startrun=test_file_for_startrun,
)


