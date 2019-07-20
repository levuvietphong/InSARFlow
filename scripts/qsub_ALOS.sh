#!/bin/bash

#SBATCH --job-name=ISF-ALOS
#SBATCH --nodes=2
#SBATCH --time=48:00:00
#SBATCH --ntasks-per-node=20
#SBATCH --output=PBS_std.out
#SBATCH --error=PBS_err.out
#SBATCH --partition=workq
ulimit -s unlimited
ulimit -l unlimited

source /home/phonglvv/.ISCE_CONFIG
config='./ALOS_parameters.cfg'
source $config
export OMP_NUM_THREADS=4
srun -n 20 $pathscript/mpi_ALOS.py -m $pmode -r $rawdir -d $ISCEdir -l $ActiveList 

# Update complete and active pairs
Check_Interferogram_ALOS.py -m $pmode -i $ISCEdir -l $DatePairList -a $ActiveList -c $CompleteList
