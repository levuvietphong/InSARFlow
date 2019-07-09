#!/bin/bash

#---------------------------------------------------------------------
# This script is used for batch processing ALOS data using ISCE
# Several scripts/functions are borrowed or adapted from others
#       1. ssara_federated_query.py is from S. Baker @UNAVCO
#       2. Get_ALOSdateID.sh is adapted from the work by J. Chen @NCL
#
#---------------------------------------------------------------------
# Created by Phong Le @VNU-HUS
# Last updated: 11/20/2018
#---------------------------------------------------------------------

#--------------------------
# 0. Set up parameters
#--------------------------
processinglevel=L1.0
path=477
frame=200
abs_orbit=25419,24748,23406,18709,18038,15354,12670,11999,11328,10657,9986,8644,7302,5289,4618
parallel_scenes=2

echo "Processing InSAR ........."

#-----------------------------
# 1. Download data from ASF
#-----------------------------
flag_download=true
ALOSzip="ALOS_zip"
if $flag_download; then
    echo -e "1. Downloading ALOS data ..."
    ssara_federated_query.py -p ALOS --processingLevel=$processinglevel \
                             -r $path -f $frame -a $abs_orbit \
                             --download --parallel=$parallel_scenes
    mkdir -p $ALOSzip
    mv *.zip $ALOSzip
    echo -e "Download data finished !!!"
fi


#---------------------
# 2. Unzip data files
#---------------------
flag_unzip=false
ALOSraw="ALOS_raw"
dateID=dateID.info
if $flag_unzip; then    
    echo -e "2. Unzipping and extracting data..."
    mkdir -p $ALOSraw
    sh Get_ALOSdateID.sh $ALOSzip $ALOSraw $dateID
    Create_ALOS_xml.py -r $ALOSraw -c $dateID -o .
    
    ### Adding rawdir folder to the created isceApp.xml    
    str="<constant name="'"rawdir"'">$PWD</constant>"
    sed -i '/<component name="isce">/ a '"$str"'' isceApp.xml
    
    echo -e "Unzip finished !!!"
fi


#------------------------------------------
# 3. Preprocessing for baseline estimation
#------------------------------------------
flag_baseline=false
screenlog=screen.log
baseline_file=${PWD}/baseline.inf
thres_baseline=500
datePairFile='datePair.info'
logfile=${PWD}/ALOS_`date +%Y_%m_%d-%H_%M`.log

if $flag_baseline; then
    echo -e "3. Checking baseline ......"
    echo -e "   ISCE pre-processing for baseline..."
    if [ -f $datePairFile ] ; then
        rm $datePairFile
    fi

    echo -e "   $> isceApp.py isceApp.xml --steps --end='preprocess' ..."
    isceApp.py isceApp.xml --steps --end="preprocess" &>> $screenlog
  
    echo -e "   Calculating perpendicular baseline ..."
    if [ ! -f "isce.log" ]; then
      echo "Error: No isce.log file found!!!"
      exit 0
    fi

    cat isceProc.xml | grep -n ".perp_baseline_bottom" > $baseline_file
    cat ${baseline_file}| while read line
    do
        data=$(echo $line | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
        linenum=`echo $data | awk '{print $1}'`
        date_ii=$(sed -n $(($linenum-8))p < isceProc.xml)
        perp=`echo $data | awk '{print int($2)}'`
        perp_abs=${perp#-}
        if [ $perp_abs -lt $thres_baseline ]; then
            # conver <date1__date2> to date1/date2 to a datepair file
            echo "$date_ii : baseline = $perp"    
            datepair_str=${date_ii/__//}
            datepair_str=${datepair_str//[<>]/}
            echo ${datepair_str} >> $datePairFile
        fi
    done
    ### Re-create the isceApp.xml with updated selectPairs
    Create_ALOS_xml.py -r $ALOSraw -c $dateID -p $datePairFile -o .
    str="<constant name="'"rawdir"'">$PWD</constant>"
    sed -i '/<component name="isce">/ a '"$str"'' isceApp.xml

    echo "Finished baseline selection, update datepairs in $datePairFile"
fi

#-------------------------------------
# 4. Generating interferogram network
#-------------------------------------
flag_ifgs=false
if $flag_ifgs; then
    echo -e "4. Generating interferogram network ......"
    isceApp.py isceApp.xml --steps --start="verifyDEM"  &>> $screenlog
fi
echo "Completed...!!!"