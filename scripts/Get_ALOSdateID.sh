#!/bin/bash
##unzip ALOS zip and generate conversion between filename ID and date
#Created by J. Chen @NCL on 2017-04-27
#
##
if [ $# -lt 2 ]; then
    echo "Usage: Get_ALOSdateID.sh <zipdir> <unzipdir> [dateID.info]"
    exit 1
fi
zipdir=$1
unzipdir=$2
if [ $# -eq 3 ]; then
    dateIdFile=$3
else
    dateIdFile=dateID.info
fi

if [ ! -d ${zipdir} ]; then
    echo "Cannot find ${zipdir}"
    exit 1
fi

if [ ! -d ${unzipdir} ]; then
    mkdir ${unzipdir}
fi

# unzip
for file in ${zipdir}/ALP*.zip; do
    if [ -f $file ]; then
        unzip -o $file -d ${unzipdir}
    fi
done

# get date from workreport file
cd ${unzipdir}
if [ -f $dateIdFile ]; then
    rm -f $dateIdFile
fi
touch $dateIdFile
for folder in ./ALP*; do
    if [ -d $folder ]; then
        folder_base=`basename $folder`
        orbID=`echo | awk '{print substr("'${folder_base}'",7,5)}'`
        scene=`grep "Scs_SceneID" $folder/workreport | awk '{print substr($3,2,15)}'`
        date=`grep "Img_SceneCenterDateTime" $folder/workreport | awk '{print substr($3,2,8)}'`
        # print file orbit ID and date to file
        echo "${orbID}    ${date}    ${scene}" >> temp.info
    fi
    # Rename directory
    mv ${folder} ${date}
done
# remove the same lines
sort -n temp.info | awk '{if($0!=line)print; line=$0}' > $dateIdFile
rm -f temp.info
echo "unzipped data in ${unzipdir}"
echo "Finished!"
