#!/bin/bash

#SBATCH --job-name=ISF-SEN1A
#SBATCH --nodes=2
#SBATCH --time=48:00:00
#SBATCH --ntasks-per-node=20
#SBATCH --output=PBS_std.out
#SBATCH --error=PBS_err.out
#SBATCH --partition=workq
ulimit -s unlimited
ulimit -l unlimited

source /home/phonglvv/.ISCE_CONFIG
config='./SEN1A_parameter.cfg'
source $config
export OMP_NUM_THREADS=5
srun -n 8 $pathscript/mpi_SEN1A.py -d $ISCEdir -i $active_file