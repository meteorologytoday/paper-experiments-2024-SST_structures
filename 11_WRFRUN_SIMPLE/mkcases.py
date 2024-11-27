import numpy as np
import os
import json
import f90nml

def pleaseRun(cmd):

    print(">> ", cmd)
    os.system(cmd)

lab_name = "lab_SIMPLE"

ref_WRF_root = "/home/t2hsu/models/WRF_gcc/SST_structure_paper/WRFV4.6.0_SIMPLE"
ref_namelist = "namelist.input"
ref_caserundir = "%s/test/em_quarter_ss" % ( ref_WRF_root,)


ref_softlink_infos = [
    dict(
        dir_path = "%s/run" % (ref_WRF_root,),
        files = [
            "bulkdens.asc_s_0_03_0_9",
            "bulkradii.asc_s_0_03_0_9",
            "capacity.asc",
            "coeff_p.asc",
            "coeff_q.asc",
            "constants.asc",
            "kernels.asc_s_0_03_0_9",
            "kernels_z.asc",
            "masses.asc",
            "termvels.asc",
            "LANDUSE.TBL",
            "RRTMG_LW_DATA",
            "RRTMG_LW_DATA_DBL",
            "RRTMG_SW_DATA",
            "RRTMG_SW_DATA_DBL",
            "RRTM_DATA",
            "RRTM_DATA_DBL",
        ],
    ),

    dict(
        dir_path = "%s/main" % (ref_WRF_root,),
        files = [
            "ideal.exe",
            "wrf.exe",
        ],
    ),


]


bl_scheme_mapping = dict(
    YSU    = 1,
    MYNN25 = 5,
    MYNN3  = 6,
    MYJ    = 2,
    SCHEME16 = 16,
    MYNN25_sfMYNN = 5,
)


# option: no_mp_heating
mp_heating_mapping = dict(
    on  = 0,
    off = 1,
)

sfclay_scheme_mapping = dict(
    YSU    = 1,
    MYNN25 = 1,
    MYNN3  = 1,
    MYJ    = 2,
)


f0    = 1e-4
T0    = 273.15 + 15.0
dx = 2000.0 # 2km
dy = 2000.0 # 2km
Nx = 1000
bl_scheme = ["MYNN25",]
mp_heating = ["off"]

BIGSELECTOR = "VARY_LX_AND_US"
print("!!!!!!!!! BIGSELECTOR = ", BIGSELECTOR)

if BIGSELECTOR == "VARY_LX_AND_US":

    bl_scheme = ["MYNN25", "MYJ", "YSU", ]
    Us    = np.array([20,], dtype=float)
    dTs    = np.array([0.0, 0.5, 1, 1.5, 2, 2.5, 3.0], dtype=float)
    wnms = np.array([0, 4, 5, 7, 10, 20, 40,], dtype=float) 

else:

    raise Exception("Unknown BIGSELECTOR = %s" % (str(BIGSELECTOR),))




# parallelization
parallel_N = 4


sim_cases = []


nml = f90nml.read(ref_namelist)

# Setup cases configuration
for i, dT in enumerate(dTs):
    #for j, Lx in enumerate(Lxs):
    for j, wnm in enumerate(wnms):
        for k, U in enumerate(Us):
            for m, _bl_scheme in enumerate(bl_scheme):
                for n, _mp_heating in enumerate(mp_heating):


                    #if Lx % dx != 0:
                    #    raise Exception("Lx mod dx != 0. We get: Lx=%f, dx=%f" % (Lx, dx))

                    if wnm not in [4, 10] and dT not in [0, 1, 3]:
                        continue


                    if dT == 0 and wnm != 0:
                        continue
                    
                    if wnm == 0 and dT != 0:
                        continue


                    sim_cases.append({
                        'casename' : "case_mph-%s_wnm%03d_U%02d_dT%03d_%s" % (_mp_heating, wnm, U, dT*1e2, _bl_scheme),
                        'casename_short' : "DRYm%sw%03dU%02ddT%03d%s" % (_mp_heating, wnm, U, dT*1e2, _bl_scheme),
                        'T0'         : T0,
                        'dT'         : dT,
                        'wnm'        : wnm,
                        'dx'         : dx,
                        'Nx'         : Nx,
                        'U'          : U,
                        'f0'         : f0,
                        'bl_scheme'  : _bl_scheme,
                        'mp_heating' : _mp_heating,
                    })


# Generate vertical profiles

def getSoundingFilename(U):
    return "sounding_files/sounding_U%d.ref" % (U,)
            
for U in Us:
    print("Generate vertical profile of U=%d" % (U,))
    filename = getSoundingFilename(U)
    if os.path.exists(filename):
        print("File %s already exist." % filename)
    else:
        print("File %s does not exist. Generate it now..." % (filename,) )
        pleaseRun("../01_sounding/gen_sounding.sh %d" % (U,))

# Generate cases
for i, sim_case in enumerate(sim_cases):

    print("Generating case %d : %s" % (i, sim_case['casename'], ))

    case_folder = '%s/%s' % (lab_name, sim_case['casename'],)

    if os.path.isdir(case_folder):
        print("Folder %s already exists. Skip it!" % (case_folder,))
    else:
        
        print("Folder %s not exists. Make it!" % (case_folder,))

        pleaseRun("mkdir -p %s" % (case_folder,) )

        for ref_softlink_info in ref_softlink_infos:
            
            for fname in ref_softlink_info['files']:
                pleaseRun("ln -s %s/%s %s/" % (ref_softlink_info["dir_path"], fname, case_folder))


        sounding_filename = getSoundingFilename(sim_case["U"])
        pleaseRun("cp %s %s/input_sounding" % (sounding_filename, case_folder,))

        pleaseRun("cp tools/* %s/" % (case_folder,))
        pleaseRun("cp %s %s/namelist_unmodified.input" % (ref_namelist, case_folder,))

        pleaseRun("f90nml -p -g physics -v bl_pbl_physics=%d -v sf_sfclay_physics=%d  -v no_mp_heating=%d -v ra_lw_physics=0 -v ra_sw_physics=0 -v mp_physics=1 %s/namelist_unmodified.input > %s/namelist.tmp" % (
            bl_scheme_mapping[sim_case['bl_scheme']],
            sfclay_scheme_mapping[sim_case['bl_scheme']],
            mp_heating_mapping[sim_case['mp_heating']],
            case_folder,
            case_folder,)
        )

        pleaseRun("f90nml -p -g domains -v e_we=%d -v dx=%f %s/namelist.tmp > %s/namelist.input" % (
            sim_case["Nx"] + 1,
            sim_case["dx"],
            case_folder,
            case_folder,
        ))

        # Write settings
        with open('%s/run_setting.json' % (case_folder,), 'w', encoding='utf-8') as f:
            json.dump(sim_case, f, ensure_ascii=False, indent=4)

    for partition, memory in [
        ["cw3e-compute", "40G",],
        ["cw3e-shared",  "20G",],
    ]: 
        with open('%s/submit_%s.sh' % (case_folder, partition), 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
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

source /home/t2hsu/.bashrc_WRF_gcc


local_scratch=/scratch/${{USER}}/job_${{SLURM_JOBID}}


echo "Local scratch    : $local_scratch"
echo "SLURM_SUBMIT_DIR : $SLURM_SUBMIT_DIR"


echo "Copying files to local scratch"

ls | grep -v -e wrfout -e wrfrst -e ".err" -e ".out" | xargs -I % cp % -t $local_scratch

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

""".format(jobname=sim_case['casename_short'], partition=partition, memory=memory))



