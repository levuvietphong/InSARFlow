#!/bin/bash

source /home/phonglvv/.ISCE3_CONFIG
config='./ALOS_parameters.cfg'
source $config
logbash='stack_logs.txt'
touch $logbash

DEMdir=DEM
mkdir -p $DEMdir

cd $DEMdir
dem.py -a stitch -b $minLat_int $maxLat_int $minLon_int $maxLon_int -r -c    
wbd.py $minLat_int $maxLat_int $minLon_int $maxLon_int
fixImageXml.py -f -i demLat_*.dem.wgs84
cd ..
