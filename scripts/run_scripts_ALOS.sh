#!/bin/bash

#------------------------------------------------------------------------------
# This script is designed for batch processing SAR data using ISCE. Message 
# Passing Interface (MPI) in Python is used for parallel processing insarApp.py
# in multiple compute nodes.
#---------------------------------------------------------------------
# Created by Phong Le @VNU-HUS
# Last updated: 11/20/2018
#---------------------------------------------------------------------

echo "PROCESSING ALOS InSAR USING ISCE ......"

#-----------------------------------------------------
# 0. SETUP PARAMETERS
#    Select sensor, processing level, path, frame, 
#    and list of orbit
#-----------------------------------------------------
config='./ALOS_parameters.cfg'
source $config
logbash='bash_logs.txt'
touch $logbash

mkdir -p $zipdir
mkdir -p $rawdir
mkdir -p $ISCEdir
mkdir -p $GIAnTdir
mkdir -p $MISCdir

#--------------------------------------------------------
# 1. DOWNLOAD SAR RAW DATA
#    - Data can be downloaded automatically using script 
#    by ASF (flag_asf=true) or the SSARA (false)
#--------------------------------------------------------
if $flag_download; then
    echo -e "1. Downloading ALOS data ... " | tee -a "$logbash"
    # Use Alaska Satellite Facilities script
    download_ASFdata.py -i $asf_data_file -d $zipdir
    echo -e "Download data finished !!!" | tee -a "$logbash"
fi


#--------------------------------------------------------------
# 2. UNZIP RAW DATA FILES
#    - Extract zip files into rawdir folder using Get_ALOSdateID.sh
#    and then obtain date information. 
#    - Default folders are renamed to corresponding dates
#--------------------------------------------------------------
if $flag_unzip; then    
    echo -e "2. Unzipping and extracting data..." | tee -a "$logbash"
    sh $scriptdir/Get_ALOSdateID.sh $zipdir $rawdir $dateID
    echo -e "Unzip finished !!!" | tee -a "$logbash"
fi


#--------------------------------------------------------------
# 3. PRE-PROCESSING FOR BASELINE ESTIMATION
#    - We use isceApp.py for preprocessing info, downloading DEM,
#    and estimating baseline conditions. Pairs of scenes are
#    then selected for parallel processing using insarApp.py
#    - Date pairs information is stored at 'DatePairList'.
#    - Directories of selected pairs are stored in 'listxml'.
#    - Two files named 'Baseline_table.csv' and 'ifg.list' will be created.
#    - Note: Networkx package should be installed for this task.
#--------------------------------------------------------------
if $flag_baseline; then
    echo -e "3. Checking baseline ......" | tee -a "$logbash"
    echo -e "   ISCE pre-processing for baseline..." | tee -a "$logbash"

    # Download STRM DEM files
    # In coastal region, sometimes downloading is failed because some tiles are in ocean (no data)
    # In this case, let isceapp downloads the DEM automatically.
    cd $ISCEdir
    dem.py -a stitch -b $minLat_int $maxLat_int $minLon_int $maxLon_int -r -c    
    cd ..
    demfile="$(basename "$(ls $ISCEdir/*.wgs84)")"

    # Run preprocessing for baseline estimation info
    # This task will create folders and calculate information for all possible combinations among scenes.    
    # Create isceApp.xml file for ISCE preprocessing all scenes and and input_swbd.xml for water mask
    export OMP_NUM_THREADS=$omp_threads
    if [ -z "$demfile" ]; then
        # No DEM file found, ISCE will download dem
        GenerateISCE_XML_ALOS.py -m $pmode -r $rawdir -c $dateID -i $ISCEdir --bbox $minLat_int,$maxLat_int,$minLon_int,$maxLon_int 
        isceApp.py isceApp.xml --steps --end="verifyDEM" >> $screenlog
    else
        # Dem files found, skip do verifyDEM
        GenerateISCE_XML_ALOS.py -m $pmode -r $rawdir -c $dateID -i $ISCEdir -d $demfile --bbox $minLat_int,$maxLat_int,$minLon_int,$maxLon_int 
        isceApp.py isceApp.xml --steps --end="preprocess" >> $screenlog
    fi

    # Download water body data mask    
    demfile="$(basename "$(ls $ISCEdir/*.wgs84)")"       
    Generate_SWBD_xml.py -i $ISCEdir -d $demfile
    cd $ISCEdir
    wbdStitcher.py input_swbd.xml
    cd ..

    # Estimate temporal and perpendicular baselines
    echo -e "   Calculating perpendicular baseline ..." | tee -a "$logbash"
    Baseline_ALOS_checking.py -d $ISCEdir -i isceProc.xml -l $ifglist -o $DatePairList -s $scenefile -t $temp_bsln -p $perp_bsln -a $rawdir/$dateID
fi

#--------------------------------------------------------------
# 4. REMOVING PAIRS THAT ARE NOT SATISFIED BASELINE CONDITIONS
#    - Remove all folders that are not satisfied pairs    
#--------------------------------------------------------------
if $flag_rup; then
    echo -e "   Removing unused folders and files ..." | tee -a "$logbash"
    Clean_Unused_Pairs_ALOS.py -i $ISCEdir -s $scenefile -p $DatePairList
fi

#----------------------------------------------
# 5. CREATING insarApp.xml FILES FOR EACH PAIR
#----------------------------------------------
if $flag_insar; then
    # Creat insar_date1_date2.xml files in corresponding folders 
    demfile="$(basename "$(ls $ISCEdir/*.wgs84)")"
    Create_XMLfiles_ALOS.py -m $pmode -r $rawdir -i $ISCEdir -p $DatePairList -d $demfile

    # Copy DEM files if exist to each folder
    while IFS= read -r line
    do
        cp $ISCEdir/dem* $ISCEdir/$line
        cp $ISCEdir/swbd* $ISCEdir/$line
        printf 'Copy DEM and SWBD files to %s \n' "$line"
    done <"$DatePairList"

    echo "Finished baseline selection, update datepairs in $DatePairList" | tee -a "$logbash"
fi

#----------------------------------------------
# 6. RUNNING insarApp.py IN PARALLEL USING MPI
#----------------------------------------------
if $flag_ifgs; then
    echo -e "4. Generating interferogram network in parallel ......" | tee -a "$logbash"
    
    # Check completed pairs - Only run for pairs that are incompleted
    echo -e "   ... Checking completed pairs" | tee -a "$logbash"
    Check_Interferogram_ALOS.py -m $pmode -i $ISCEdir -l $DatePairList -a $ActiveList -c $CompleteList

    # This tasks will be run in parallel in compute nodes.
    # The sbatch command will submit the job with configurations as shown in the insar_mpi.sh file.
    # sbatch insar_mpi.sh
    export OMP_NUM_THREADS=4
    srun -n 5 mpiALOS.py -m $pmode -r $rawdir -i $ISCEdir -l $ActiveList 
    
    # Update complete and active pairs
    Check_Interferogram_ALOS.py -m $pmode -i $ISCEdir -l $DatePairList -a $ActiveList -c $CompleteList
fi

#---------------------------------------------------
# 7. PREPARING ROIPAC FORMAT FILES AND BOUNDING BOX
#---------------------------------------------------
if $flag_rpac; then
    if [ -f $ifglist ]; then
        mv $ifglist $GIAnTdir/
    fi
    
    # Extracting info for GIAnT processing
    echo -e "Running rpac_scan.py ......" | tee -a "$logbash"
    PrepareRoipac_ALOS.py -m $pmode -i $ISCEdir -l $DatePairList -g $GIAnTdir -b $bbox -c 0
    
    # Create insarApp.xml again with re-geocoding
    echo -e "Running Create_insar_ALOS_xml.py ......" | tee -a "$logbash"
    demfile="$(basename "$(ls $ISCEdir/*.wgs84)")"
    Create_XMLfiles_ALOS.py -m $pmode -r $rawdir -i $ISCEdir -p $DatePairList -d $demfile -b $GIAnTdir/$bbox

    # Run geocoding using mpi
    echo -e "Running re-geocoding ......" | tee -a "$logbash"
    export OMP_NUM_THREADS=12
    srun -n 20 mpi_geocode_ALOS.py -m $pmode -i $ISCEdir -l $DatePairList -g $GIAnTdir

    # Update cropping information
    echo -e "Running PrepareRoipac again......" | tee -a "$logbash"
    PrepareRoipac_ALOS.py -m $pmode -i $ISCEdir -l $DatePairList -g $GIAnTdir -b $bbox -c 0
fi


#---------------------------------------------------
# 8. REMOVING FILES UNNECESSARY IN GIANT
#---------------------------------------------------
if $flag_clean; then
    Clean_All_Files_Unused.py -m $pmode -r $rawdir -c $dateID -i $ISCEdir -l $DatePairList
    echo -e "Cleaning unnecessary files complete......" | tee -a "$logbash"
fi    

echo "Completed...!!!"  | tee -a "$logbash"
