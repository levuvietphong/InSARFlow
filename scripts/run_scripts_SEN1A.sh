#!/bin/bash

#------------------------------------------------------------------------------
# This script is designed for batch processing inSAR data using ISCE. Message 
# Passing Interface (MPI) in Python is used for parallel processing topsApp.py
# in multiple compute nodes.
#---------------------------------------------------------------------
# Created by Phong Le @VNU-HUS
# Last updated: 4/4/2019
#---------------------------------------------------------------------

echo "PROCESSING DInSAR USING ISCE ......"

#-----------------------------------------------------
# 0. SETUP PARAMETERS
#    Select sensor, processing level, path, frame, 
#    and list of orbit
#-----------------------------------------------------
config='./SEN1A_parameter.cfg'
source $config
logbash='bash_logs.txt'
touch $logbash

mkdir -p $slcdir
mkdir -p $auxdir
mkdir -p $poedir
mkdir -p $ISCEdir
mkdir -p $GIAnTdir
mkdir -p $MISCdir

# DOWNLOADING DATA
if $flag_download; then
    echo -e "1. DOWNLOADING SENTINEL-1A DATA FROM ASF ... " | tee -a "$logbash"
    download_ASFdata.py -i $asf_data_file -d $slcdir \
                        -a $auxdir -l $auxlink -p $poedir
    echo -e "Download data completed !!!" | tee -a "$logbash"
fi


# CHECKING DEM AND CREATING XML FILES
if $flag_topsar; then
    echo -e "2. CHECKING TEMPORAL BASELINE FOR PAIRING IFGs ... " | tee -a "$logbash"
    # Check temporal baseline
    Baseline_SEN1A_check.py -i $asf_data_file -d $ISCEdir -p $DatePairList -t $temp_bsln
    
    # Downloading and stitching DEM files
    cd $ISCEdir
    dem.py -a stitch -b $minLat_int $maxLat_int $minLon_int $maxLon_int -r -c -k
    cd ..

    # Create xml file for first pair for verifyDEM purpose
    demfile="$(basename "$(ls $ISCEdir/*.wgs84)")"
    Create_insar_SEN1A_xml.py   -s $slcdir -i $ISCEdir -a $auxdir \
                                -l $auxlink -o $poedir -p $DatePairList \
                                -b $minLat,$maxLat,$minLon,$maxLon \
                                -d $demfile
    
    # Copy corrected DEM to each pair
    while IFS= read -r line
    do
        cp $ISCEdir/dem* $ISCEdir/$line
        printf 'Copy DEM files to %s.\n' "$line"
    done <"$DatePairList"

    echo -e "Creating XML files completed !!! \n\n" | tee -a "$logbash"
fi


# CHECKING EXISTING IFGS & RUNNING TOPSAPP APPLICATION
if $flag_ifgs; then
    echo -e "3. CHECKING EXISTING PAIRS AND RUNNING ISCE ... " | tee -a "$logbash"
    
    #------------------------------------------------------------------------
    # Check result file in each pair's directory stored in $DatePairList
    # If all important files are found, no processing is implemented
    # If missing any file, the ifgs will be processed
    # Information of pairs that need to be processed is stored in $ActiveList
    #------------------------------------------------------------------------
    Check_Interferogram_SEN1A.py -i $ISCEdir -l $DatePairList -a $ActiveList -c $CompleteList

    #-------------------------------------------
    # Run topsApp.py processing in parallel 
    # Only run pairs listed in the $ActiveList
    #-------------------------------------------
    # ... Submit jobs to sbatch
    sbatch $pathscript/qsub_SEN1A.sh
    
    # ... OR run jobs on an interactive node
    # export OMP_NUM_THREADS=4
    # srun -n 8 $pathscript/mpi_SEN1A.py -d $ISCEdir -i $active_file

    # Update complete and active pairs
    Check_Interferogram_SEN1A.py -i $ISCEdir -l $DatePairList -a $ActiveList -c $CompleteList
fi


# PREPARING FILE IN ROIPAC FORMAT FOR GIANT
if $flag_rpac; then
    # Extracting info for GIAnT processing
    echo -e "Preparing file for GIANT using ROIPAC format ......" | tee -a "$logbash"
    PrepareRoipac_SEN1A.py -i $ISCEdir -g $GIAnTdir -l $DatePairList
fi

echo "COMPLETED...!!!"  | tee -a "$logbash"
