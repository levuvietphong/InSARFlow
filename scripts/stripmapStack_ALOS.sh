#!/bin/bash

#SBATCH --job-name=SMStack
#SBATCH --nodes=4
#SBATCH --time=06:00:00
#SBATCH --ntasks-per-node=20
#SBATCH --output=SM_std.out
#SBATCH --error=SM_err.out
#SBATCH --partition=workq
ulimit -s unlimited
ulimit -l unlimited

source /home/phonglvv/.ISCE3_CONFIG

#------------------------------------------------------------------------------
# This script is designed for processing ALOS data using stripmapStack in ISCE. 
#---------------------------------------------------------------------
# Created by Phong Le @VNU-HUS
# Last updated: 8/29/2019
#---------------------------------------------------------------------

echo "PROCESSING ALOS InSAR USING STRIPMAPSTACK IN ISCE ......"
echo "working directory = "$SLURM_SUBMIT_DIR
cd $SLURM_SUBMIT_DIR

#-----------------------------------------------------
# 0. SETUP PARAMETERS
#    Select sensor, processing level, path, frame, 
#    and list of orbit
#-----------------------------------------------------
config='./ALOS_parameters.cfg'
source $config
logbash='stack_logs.txt'
touch $logbash

SLCdir=SLCs
DEMdir=DEM

mkdir -p $SLCdir
mkdir -p $DEMdir

# cd $DEMdir
# dem.py -a stitch -b $minLat_int $maxLat_int $minLon_int $maxLon_int -r -c    
# wbd.py $minLat_int $maxLat_int $minLon_int $maxLon_int
# fixImageXml.py -f -i demLat_*.dem.wgs84
# cd ..

prepRawALOS.py -i $zipdir -o $SLCdir -t '' --dual2single
srun -n 20 ~/InSARFlow/scripts/InSARFlowStack.py -i run_unPackALOS

master=$(ls $SLCdir | head -1)
stackStripMap.py -s $SLCdir -d $DEMdir/demLat_*.dem.wgs84 -t 700 -b 2000 -a 20 -r 8 -u snaphu -W interferogram -m $master -f 0.5

logfile='logs.txt'
cd run_files
chmod +x *
echo -e "Running run_1_master" | tee -a "$logfile"
./run_1_master

echo -e "Running run_2_focus_split" | tee -a "$logfile"
srun -n 40 ~/InSARFlow/scripts/InSARFlowStack.py -i run_2_focus_split

echo -e "Running run_3_geo2rdr_coarseResamp" | tee -a "$logfile"
srun -n 20 ~/InSARFlow/scripts/InSARFlowStack.py -i run_3_geo2rdr_coarseResamp

echo -e "Running run_4_refineSlaveTiming" | tee -a "$logfile"
srun -n 40 ~/InSARFlow/scripts/InSARFlowStack.py -i run_4_refineSlaveTiming

echo -e "Running run_5_invertMisreg" | tee -a "$logfile"
./run_5_invertMisreg

echo -e "Running run_6_fineResamp" | tee -a "$logfile"
srun -n 20 ~/InSARFlow/scripts/InSARFlowStack.py -i run_6_fineResamp

echo -e "Running run_7_grid_baseline" | tee -a "$logfile"
srun -n 20 ~/InSARFlow/scripts/InSARFlowStack.py -i run_7_grid_baseline

echo -e "Running run_8_igram" | tee -a "$logfile"
srun -n 40 ~/InSARFlow/scripts/InSARFlowStack.py -i run_8_igram

cd ..

slavedir=$(ls ./coregSLC/Coarse/ | head -1)
cp -r coregSLC/Coarse/$slavedir/masterShelve .
run_multilook_geometry 20 8
prep_isce.py -i ./Igrams -m ./masterShelve/data.dat -b ./baselines -g ./geom_master
