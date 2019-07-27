#!/bin/bash

#SBATCH --job-name=ISF-GIAnT
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --ntasks-per-node=20
#SBATCH --output=GIAnT_std.out
#SBATCH --error=GIAnT_err.out
#SBATCH --partition=workq
ulimit -s unlimited
ulimit -l unlimited

source /home/phonglvv/.giant/.giant2env
pathscript=$1
config=$2
platform=$3

sh $pathscript/run_GIAnT.sh $config $platform