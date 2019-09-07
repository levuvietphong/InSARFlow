#!/bin/bash

#SBATCH --job-name=ISF-SEN1A
#SBATCH --nodes=20
#SBATCH --time=12:00:00
#SBATCH --ntasks-per-node=20
#SBATCH --output=PBS_std.out
#SBATCH --error=PBS_err.out
#SBATCH --partition=workq
ulimit -s unlimited
ulimit -l unlimited

source /home/phonglvv/.ISCE_CONFIG
config='./SEN1A_parameters.cfg'
source $config
export OMP_NUM_THREADS=4
srun -n 100 $pathscript/mpi_SEN1A.py -d $ISCEdir -i $ActiveList

# Update complete and active pairs
Check_Interferogram_SEN1A.py -i $ISCEdir -l $DatePairList -a $ActiveList -c $CompleteList
