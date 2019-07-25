#!/bin/bash

if [ -z "$1" ]
  then
    echo "No config file supplied in run_GIANT.sh! Please check!!!"
    echo "EXIT!!!"
    exit 1
fi

config=$1
platform=$2

source ../$config
loggiant='logs_giant.txt'
touch $loggiant

if $preparexml; then
    echo -e $(date '+%d/%m/%Y %H:%M:%S') | tee -a "$loggiant"
    if [ $platform == "Sentinel-1A" ]; then
        echo -e "Running ./prepxml_SBAS_SEN1A.py ... " | tee -a "$loggiant"
        ./prepxml_SBAS_SEN1A.py >> goutput.txt
    else
        echo -e "Running ./prepxml_SBAS_ALOS.py ... " | tee -a "$loggiant"
        ./prepxml_SBAS_ALOS.py >> goutput.txt
    fi
fi


if $igram; then
    echo -e $(date '+%d/%m/%Y %H:%M:%S') | tee -a "$loggiant"
    echo -e "Running ./PrepIgramStack.py ... " | tee -a "$loggiant"
    PrepIgramStack.py >> goutput.txt
fi


if $stack; then
    echo -e $(date '+%d/%m/%Y %H:%M:%S') | tee -a "$loggiant"
    echo -e "Running ./ProcessStack.py ... " | tee -a "$loggiant"
    ProcessStack.py >> goutput.txt
fi 

if $invert; then
    echo -e $(date '+%d/%m/%Y %H:%M:%S') | tee -a "$loggiant"
    if [ $method=="nsbas" ]; then
        echo -e "Running ./NSBASInvert.py ... " | tee -a "$loggiant"
        NSBASInvert.py >> goutput.txt
    else          
        echo -e "Running ./SBASInvert.py ... " | tee -a "$loggiant"
        SBASInvert.py >> goutput.txt
    fi
fi