#!/bin/bash

#SBATCH --job-name=STACK-SEN
#SBATCH --nodes=2
#SBATCH --time=48:00:00
#SBATCH --ntasks-per-node=20
#SBATCH --output=PBS_std.out
#SBATCH --error=PBS_err.out
#SBATCH --partition=workq
ulimit -s unlimited
ulimit -l unlimited

export OMP_NUM_THREADS=4
source /home/phonglvv/.ISCE_CONFIG
logfile='logs.txt'

echo -e "Running run_1_unpack_slc_topo_master" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_1_unpack_slc_topo_master

echo -e "Running run_2_average_baseline" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_2_average_baseline

echo -e "Running run_3_extract_burst_overlaps" | tee -a "$logfile"
./run_3_extract_burst_overlaps

echo -e "Running run_4_overlap_geo2rdr_resample" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_4_overlap_geo2rdr_resample

echo -e "Running run_5_pairs_misreg" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_5_pairs_misreg

echo -e "Running run_6_timeseries_misreg" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_6_timeseries_misreg

echo -e "Running run_7_geo2rdr_resample" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_7_geo2rdr_resample

echo -e "Running run_8_extract_stack_valid_region" | tee -a "$logfile"
./run_8_extract_stack_valid_region

echo -e "Running run_9_merge_burst_igram" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_9_merge_burst_igram

echo -e "Running run_10_filter_coherence" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_10_filter_coherence

echo -e "Running run_11_unwrap" | tee -a "$logfile"
srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_11_unwrap

# echo -e "Running run_12_merge_master_slave_slc" | tee -a "$logfile"
# srun -n 10 ~/InSarFlow/scripts/InSARFlowStack.py -i run_12_merge_master_slave_slc